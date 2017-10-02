from flask import Flask, json, request

from . import settings


app = Flask(__name__)


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def route(path):
    def to_json(data):
        if 'pretty' in request.args:
            return json.dumps(data, indent=4) + '\n'
        return json.dumps(data)

    if request.method == 'GET':
        try:
            data = settings.get(path, serialized=True)
        except (KeyError, ValueError) as e:
            return str(e), 400
    elif request.method == 'POST':
        try:
            data = settings.set(path, request.get_json())
        except (KeyError, ValueError) as e:
            return str(e), 400
    return to_json(data)


@app.route('/xkcd')
def xkcd():
    return 'https://c.xkcd.com/random/comic\n'
