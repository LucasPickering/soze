from flask import json, request

from .. import app
from . import user_settings


def to_json(data):
    if 'pretty' in request.args:
        return json.dumps(data, indent=4) + '\n'
    return json.dumps(data)


@app.route('/')
def root():
    return to_json(user_settings.to_dict())


@app.route('/xkcd')
def xkcd():
    return 'https://c.xkcd.com/random/comic'


@app.route('/led', methods=['GET', 'POST'])
def led():
    if request.method == 'GET':
        return to_json(user_settings.to_dict()['led'])
    elif request.method == 'POST':
        data = request.get_json()
        if 'mode' in data:
            user_settings.set_led_mode(data['mode'])
        if 'static_color' in data:
            user_settings.set_led_static_color(data['static_color'])
        return "Success"


@app.route('/led/fade', methods=['GET', 'POST'])
def led_fade():
    if request.method == 'GET':
        return to_json(user_settings.to_dict()['led']['fade'])
    elif request.method == 'POST':
        data = request.get_json()
        if 'mode' in data:
            user_settings.set_led_mode(data['mode'])
        if 'static_color' in data:
            user_settings.set_led_static_color(data['static_color'])
        return "Success"


@app.route('/lcd', methods=['GET', 'POST'])
def lcd():
    if request.method == 'GET':
        return to_json(user_settings.to_dict()['lcd'])
    elif request.method == 'POST':
        data = request.get_json()
        if 'mode' in data:
            user_settings.set_lcd_mode(data['mode'])
        if 'color' in data:
            user_settings.set_lcd_color(data['color'])
        return "Success"
