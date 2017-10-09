import argparse
import json
import os
import requests
from pprint import pprint
from configparser import SafeConfigParser

CFG_FILE = os.path.expanduser('~/.ccc.ini')
CFG_SECTION = 'all'
DEFAULT_CFG = {'host': 'localhost', 'port': 5000}
COMMANDS = {}


def command(name, *cmd_args, **kwargs):
    def inner(func):
        def wrapper(*args):
            func(*args)
        COMMANDS[name] = (func, cmd_args, kwargs)
        return wrapper
    return inner


def get_url(setting):
    host = cfg['host']
    port = cfg['port']
    route = setting.replace('.', '/')
    return f'http://{host}:{port}/{route}'


def get(setting):
    url = get_url(setting)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def post(setting, value):
    url = get_url(setting)
    response = requests.post(url, json=value)
    response.raise_for_status()
    return response.json()


def parse_settings(settings):
    return (tuple(setting.split('=', 1)) for setting in settings)


@command('get', (['settings'],
                 {'nargs': '*', 'help': "Settings to get the value of, e.g. 'led.mode' -> 'off'"}),
         help="Get one or more settings")
def get_settings(settings):
    if not settings:
        settings = ['']
    for setting in settings:
        pprint(get(setting))


@command('set', (['settings'], {'nargs': '+', 'help': "Settings to change, e.g. 'led.mode=off'"}),
         help="Set one or more settings")
def set_settings(settings):
    for setting, value in parse_settings(settings):
        try:
            json_val = json.loads(value)
        except json.decoder.JSONDecodeError:
            json_val = value

        pprint(post(setting, json_val))


@command('add-colors', (['colors'], {'nargs': '+', 'help': "Color(s) to add to the active fade"}),
         help="Add color(s) to the active fade")
def add_color(colors):
    fade_colors = get('led.fade.colors')
    fade_colors += colors
    post('led.fade.colors', fade_colors)
    print(fade_colors)


@command('del-colors', (['indexes'], {'type': int, 'nargs': '+',
                                      'help': "Index(es) of the color(s) to remove"}),
         help="Delete color(s) from the active fade")
def del_color(indexes):
    fade_colors = get('led.fade.colors')

    # Pop off items, starting at the back so we don't affect lower indexes
    for index in sorted(indexes, reverse=True):
        fade_colors.pop(index)
    post('led.fade.colors', fade_colors)
    print(fade_colors)


@command('clear-colors', help="Clear all colors from the active fade")
def clear_colors():
    post('led.fade.colors', [])
    print("Cleared")


@command('load-fade', (['name'], {'help': "Name of the fade to load"}), help="Load a fade")
def load_fade(name):
    fade = get('led.fade')
    try:
        colors = fade['saved'][name]
    except KeyError:
        print(f"No fade by the name '{name}'")
        return
    fade['colors'] = colors
    post('led.fade', fade)
    print(colors)


@command('save-fade', (['name'], {'help': "Name for the fade (will overwrite)"}),
         help="Save the current fade colors")
def save_fade(name):
    fade = get('led.fade')
    colors = fade['colors']
    fade['saved'][name] = colors
    post('led.fade', fade)
    print(f"Saved {colors} as '{name}'")


@command('del-fade', (['names'], {'nargs': '+', 'help': "Name(s) of the fade(s) to delete"}),
         help="Delete a fade")
def del_fade(name):
    saved_fades = get('led.fade.saved')
    try:
        deleted = saved_fades.pop(name)
        post('led.fade.saved', saved_fades)
        print(f"Deleted '{name}': {deleted}")
    except KeyError:
        print(f"No fade by the name '{name}'")


@command('config', (['settings'],
                    {'nargs': '*', 'help': "Config settings to change"}),
         help="Set local config value(s)")
def set_cfg(settings):
    if settings:
        cfg_dict = dict(parse_settings(settings))
        cfg.update(cfg_dict)

        # Save the config
        config = SafeConfigParser()
        config[CFG_SECTION] = cfg
        with open(CFG_FILE, 'w') as f:
            config.write(f)

    pprint(dict(cfg))


def parse_args():
    def add_subcommand(subcommand, func, **kwargs):
        subparser = subparsers.add_parser(subcommand, **kwargs)
        subparser.set_defaults(func=func)
        return subparser

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    for cmd, (func, cmd_args, kwargs) in COMMANDS.items():
        subparser = subparsers.add_parser(cmd, **kwargs)
        subparser.set_defaults(func=func)
        for arg_names, arg_kwargs in cmd_args:
            subparser.add_argument(*arg_names, **arg_kwargs)

    return parser.parse_args()


def parse_cfg():
    config = SafeConfigParser()
    config[CFG_SECTION] = DEFAULT_CFG
    config.read(CFG_FILE)
    with open(CFG_FILE, 'w') as f:
        config.write(f)
    return config[CFG_SECTION]


def main():
    argd = vars(parse_args())

    global cfg  # I'm sorry
    cfg = parse_cfg()

    try:
        func = argd.pop('func')
    except KeyError:
        print("No subcommand specified")
        exit(1)

    try:
        func(**argd)
    except requests.exceptions.HTTPError as e:
        print(f"{e}: {e.response.text}")
        exit(2)


if __name__ == '__main__':
    main()
