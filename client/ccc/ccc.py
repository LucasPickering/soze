import argparse
import json
import os
import requests
from pprint import pprint

CFG_FILE = os.path.expanduser('~/.ccc.json')
DEFAULT_CFG = {'host': 'localhost', 'port': 5000}
COMMANDS = {}


def command(*cmd_args, **kwargs):
    def inner(func):
        def wrapper(*args):
            func(*args)
        name = func.__name__.replace('_', '-')  # Hyphens are more aesthetic
        COMMANDS[name] = (func, cmd_args, kwargs)
        return wrapper
    return inner


def get_url(setting):
    host = config['host']
    port = config['port']
    route = setting.replace('.', '/')
    return f'http://{host}:{port}/{route}'


def http_get(setting):
    url = get_url(setting)

    # Print debug info
    if debug:
        print(f"GET {url}")

    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def http_post(setting, value):
    url = get_url(setting)

    # Print debug info
    if debug:
        print(f"POST {url}")
        pprint(value)

    response = requests.post(url, json=value)
    response.raise_for_status()
    return response.json()


def parse_settings(settings):
    return (tuple(setting.split('=', 1)) for setting in settings)


@command((['settings'], {'nargs': '*', 'help': "Settings to get the value of, e.g. 'led.mode'"}),
         help="Get one or more settings")
def get(settings):
    if not settings:
        settings = ['']
    for setting in settings:
        pprint(http_get(setting))


@command((['settings'], {'nargs': '+', 'help': "Settings to change, e.g. 'led.mode=off'"}),
         help="Set one or more settings")
def set(settings):
    for setting, value in parse_settings(settings):
        try:
            json_val = json.loads(value)
        except json.decoder.JSONDecodeError:
            json_val = value

        pprint(http_post(setting, json_val))


@command(help="Turn off all peripherals")
def off():
    pprint(http_post('led.mode', 'off'))
    pprint(http_post('lcd.mode', 'off'))


@command((['colors'], {'nargs': '+', 'help': "Color(s) to add to the active fade"}),
         help="Add color(s) to the active fade")
def add_colors(colors):
    fade_colors = http_get('led.fade.colors')
    fade_colors += colors
    http_post('led.fade.colors', fade_colors)
    print(fade_colors)


@command((['indexes'], {'type': int, 'nargs': '+', 'help': "Index(es) of the color(s) to remove"}),
         help="Delete color(s) from the active fade")
def del_colors(indexes):
    fade_colors = http_get('led.fade.colors')

    # Pop off items, starting at the back so we don't affect lower indexes
    for index in sorted(indexes, reverse=True):
        fade_colors.pop(index)
    http_post('led.fade.colors', fade_colors)
    print(fade_colors)


@command(help="Clear all colors from the active fade")
def clear_colors():
    http_post('led.fade.colors', [])
    print("Cleared")


@command((['name'], {'help': "Name of the fade to load"}), help="Load a fade")
def load_fade(name):
    fade = http_get('led.fade')
    try:
        colors = fade['saved'][name]
    except KeyError:
        print(f"No fade by the name '{name}'")
        return
    fade['colors'] = colors
    http_post('led.fade', fade)
    print(colors)


@command((['name'], {'help': "Name for the fade (will overwrite)"}),
         help="Save the current fade colors")
def save_fade(name):
    fade = http_get('led.fade')
    colors = fade['colors']
    saved = fade['saved']
    saved[name] = colors
    http_post('led.fade.saved', saved)
    print(f"Saved {colors} as '{name}'")


@command((['names'], {'nargs': '+', 'help': "Name(s) of the fade(s) to delete"}),
         help="Delete a fade")
def del_fade(name):
    saved_fades = http_get('led.fade.saved')
    try:
        deleted = saved_fades.pop(name)
        http_post('led.fade.saved', saved_fades)
        print(f"Deleted '{name}': {deleted}")
    except KeyError:
        print(f"No fade by the name '{name}'")


@command((['settings'], {'nargs': '*', 'help': "Config settings to change"}),
         help="Set local config value(s)")
def set_config(settings):
    if settings:
        new_cfg = dict(parse_settings(settings))  # Parse key/value pairs from the user
        config.update(new_cfg)  # Add the new settings to the config
        save_config(config)  # Save the config

    pprint(config)


def parse_args():
    def add_subcommand(subcommand, func, **kwargs):
        subparser = subparsers.add_parser(subcommand, **kwargs)
        subparser.set_defaults(func=func)
        return subparser

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default=[], action='append', help="Override config value")
    parser.add_argument('--debug', '-d', action='store_true', help="Print debug info")
    subparsers = parser.add_subparsers()

    for cmd, (func, cmd_args, kwargs) in COMMANDS.items():
        subparser = subparsers.add_parser(cmd, **kwargs)
        subparser.set_defaults(func=func)
        for arg_names, arg_kwargs in cmd_args:
            subparser.add_argument(*arg_names, **arg_kwargs)

    return parser.parse_args()


def parse_config(overrides):
    cfg = dict(DEFAULT_CFG)  # Copy the defaults to start with

    # Read the file and update our dict. Do nothing if the file doesn't exist yet.
    try:
        with open(CFG_FILE) as f:
            cfg.update(json.load(f))
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pass

    save_config(cfg)  # Write the full config back to the file
    cfg.update(overrides)  # Add in overrides now
    return cfg


def save_config(cfg):
    with open(CFG_FILE, 'w') as f:
        json.dump(cfg, f)


def main():
    argd = vars(parse_args())

    # Parse command-lien config overrides
    config_overrides = parse_settings(argd.pop('config'))

    global config  # I'm sorry
    config = parse_config(config_overrides)

    global debug
    debug = argd.pop('debug')

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
