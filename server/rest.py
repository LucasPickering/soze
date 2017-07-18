from color import Color
from flask import Flask
from flask import request

app = Flask(__name__)


def get_color(data):
    if type(data) is list and len(data) == 3:
        return Color(*data)  # Data is in a list, unpack the list into a color tuple
    raise ValueError("Invalid format for color data: {}".format(data))


@app.route('/')
def root():
    return 'This is my home: https://github.com/LucasPickering/Case-Control-CLI\n'


@app.route('/xkcd')
def xkcd():
    return 'https://c.xkcd.com/random/comic\n'


@app.route('/led', methods=['GET', 'POST'])
def led():
    if request.method == 'POST':
        data = request.get_json()
        if 'mode' in data:
            user_settings.set_led_mode(data['mode'])
        if 'static_color' in data:
            color = get_color(data['static_color'])
            user_settings.set_led_static_color(color)
        return "Success\n"
    else:
        return "GOOD SHIT GOOD SHIT\n"  # TODO print LED info


@app.route('/lcd', methods=['GET', 'POST'])
def lcd():
    if request.method == 'POST':
        data = request.get_json()
        if 'mode' in data:
            user_settings.set_lcd_mode(data['mode'])
        if 'color' in data:
            color = get_color(data['color'])
            user_settings.set_lcd_color(color)
        return "Success\n"
    else:
        return "GOOD SHIT GOOD SHIT\n"  # TODO print LCD info


def run(logger, settings, debug=False):
    # GLOBALS ARE GREAT
    global user_settings
    user_settings = settings
    app.logger = logger
    # app.run(debug=debug, host='0.0.0.0')
    app.run(host='0.0.0.0')
