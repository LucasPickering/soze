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


def command(name, *cmd_args, **kwargs):
    def inner(func):
        def wrapper(*args):
            func(*args)
        COMMANDS[name] = (func, cmd_args, kwargs)
        return wrapper
    return inner


@command('get', (['settings'],
                 {'nargs': '+', 'help': "Settings to get the value of, e.g. 'led.mode' -> 'off'"}),
         help="Get one or more settings")
def get_settings(args):
    for setting in args.settings:
        pprint(get(setting))


@command('set', (['settings'], {'nargs': '+', 'help': "Settings to change, e.g. 'led.mode=off'"}),
         help="Set one or more settings")
def set_settings(args):
    for setting_value in args.settings:
        setting, value = setting_value.split('=', 1)
        try:
            json_val = json.loads(value)
        except json.decoder.JSONDecodeError:
            json_val = value

        pprint(post(setting, json_val))


@command('load-fade', (['name'], {'help': "Name of the fade to load"}), help="Load a fade")
def load_fade(args):
    name = args.name
    fade = get('led.fade')
    try:
        colors = fade['saved'][name]
    except KeyError:
        print(f"No fade by the name '{name}'")
        return
    fade['colors'] = colors
    post('led.fade', fade)


@command('save-fade', (['name'], {'help': "Name for the fade (will overwrite)"}),
         help="Save the current fade colors")
def save_fade(args):
    name = args.name
    fade = get('led.fade')
    colors = fade['colors']
    fade['saved'][name] = colors
    post('led.fade', fade)
    print(f"Saved {colors} as '{name}'")


@command('del-fade', (['name'], {'help': "Name of the fade to delete"}), help="Delete a fade")
def del_fade(args):
    name = args.name
    saved_fades = get('led.fade.saved')
    try:
        deleted = saved_fades.pop(name)
        post('led.fade.saved', saved_fades)
        print(f"Deleted '{name}': {deleted}")
    except KeyError:
        print(f"No fade by the name '{name}'")


@command('config', (['settings'],
                    {'nargs': '+', 'help': "Config settings to change"}),
         help="Set local config value(s)")
def set_cfg(args):
    cfg_dict = dict(setting.split('=', 1) for setting in args.settings)
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
    args = parse_args()

    global cfg  # I'm sorry
    cfg = parse_cfg()

    try:
        func = args.func
    except AttributeError:
        print("No subcommand specified")
        exit(1)

    try:
        func(args)
    except requests.exceptions.HTTPError as e:
        print(f"{e}: {e.response.text}")
        exit(2)
