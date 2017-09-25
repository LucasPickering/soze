import argparse
import json
import os
import requests
from pprint import pprint
from configparser import SafeConfigParser


CFG_FILE = os.path.expanduser('~/.ccc.ini')
CFG_SECTION = 'all'
DEFAULT_CFG = {'host': 'localhost', 'port': 5000}


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


def get_settings(args):
    for setting in args.settings:
        pprint(get(setting))


def set_settings(args):
    for setting_value in args.settings:
        setting, value = setting_value.split('=', 1)
        try:
            json_val = json.loads(value)
        except json.decoder.JSONDecodeError:
            json_val = value

        pprint(post(setting, json_val))


def save_fade(args):
    name = args.name
    fade = get('led.fade')
    colors = fade['colors']
    fade['saved_fades'][name] = colors
    post('led.fade', fade)
    print(f"Saved {colors} as '{name}'")


def del_fade(args):
    name = args.name
    saved_fades = get('led.fade.saved_fades')
    try:
        deleted = saved_fades.pop(name)
        post('led.fade.saved_fades', saved_fades)
        print(f"Deleted '{name}': {deleted}")
    except KeyError:
        print(f"No fade by the name '{name}'")


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

    parser_get = add_subcommand('get', get_settings, help="Get one or more CC settings")
    parser_get.add_argument('settings', nargs='+',
                            help="Settings to get the value of, e.g. 'led.mode' -> 'static'")

    parser_get = add_subcommand('set', set_settings, help="Set one or more CC settings")
    parser_get.add_argument('settings', nargs='+',
                            help="Settings to change, e.g. 'led.mode=static'")

    parser_save_fade = add_subcommand('save-fade', save_fade, help="Save the current fade colors")
    parser_save_fade.add_argument('name', help="Name for the fade (will overwrite)")

    parser_del_fade = add_subcommand('del-fade', del_fade, help="Delete a fade")
    parser_del_fade.add_argument('name', help="Name of the fade to delete")

    parser_cfg = add_subcommand('config', set_cfg, help="Set local config value(s)")
    parser_cfg.add_argument('settings', nargs='+',
                            help="Settings to get the value of, e.g. 'led.mode' -> 'static'")

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
    cfg = parse_cfg(args.config)

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
