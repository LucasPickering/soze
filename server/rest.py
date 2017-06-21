import model
from flask import Flask
from flask import request

app = Flask(__name__)


def get_color(data):
    if type(data) is list and len(data) == 3:
        # Data is in a list, unpack the list into a color tuple
        return model.Color(*data)
    raise ValueError("Invalid format for color data: {}".format(data))


@app.route('/')
def root():
    return 'This is my home: https://github.com/LucasPickering/Case-Control-CLI\n'


@app.route('/xkcd')
def xkcd():
    return 'https://c.xkcd.com/random/comic\n'


@app.route('/led/')
def led():
    # TODO return LED info
    pass


@app.route('/led/color', methods=['GET', 'POST'])
def led_color():
    if request.method == 'POST':
        data = request.get_json()
        try:
            color = get_color(data['color'])
        except KeyError:
            return "Missing attribute 'color'\n"
        user_settings.led_static_color = color
        return "Set LED color to {}\n".format(color)
    else:
        return user_settings.led_static_color


@app.route('/lcd/')
def lcd():
    # TODO return LCD info
    pass


@app.route('/lcd/color')
def lcd_color():
    # TODO set LCD color
    pass


@app.route('/lcd/text')
def lcd_text():
    # TODO set LCD text
    pass


def run(settings, debug=False):
    # GLOBALS ARE GREAT
    global user_settings
    user_settings = settings
    app.run(debug=debug, host='0.0.0.0')
