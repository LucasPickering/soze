from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'This is my home: https://github.com/LucasPickering/Case-Control-CLI'


@app.route('/xkcd')
def xkcd():
    return 'https://xkcd.com/random/comic'


@app.route('/lcd/')
def lcd():
    # TODO return LCD info
    pass


@app.route('/lcd/text')
def lcd_text():
    # TODO set LCD text
    pass


@app.route('/lcd/color')
def lcd_color():
    # TODO set LCD color
    pass


if __name__ == '__main__':
    app.run()
