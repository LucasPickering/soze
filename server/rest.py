from flask import Flask

app = Flask(__name__)


@app.route('/')
def root():
    return 'This is my home: https://github.com/LucasPickering/Case-Control-CLI\n'


@app.route('/xkcd')
def xkcd():
    return 'https://c.xkcd.com/random/comic\n'


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


def run(mdl, debug=False):
    global model
    model = mdl
    app.run(debug=debug, host='0.0.0.0')
