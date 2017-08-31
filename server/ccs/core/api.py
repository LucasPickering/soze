from flask import json, request

from ccs import app, logger
from .settings import Settings

_SETTINGS = Settings()


def _to_json(data):
    if 'pretty' in request.args:
        return json.dumps(data, indent=4) + '\n'
    return json.dumps(data)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def route(path):
    if request.method == 'GET':
        data = _SETTINGS.get(path)
        return _to_json(data)
    elif request.method == 'POST':
        data = _SETTINGS.set(path, request.get_json())
        return _to_json(data)


@app.route('/xkcd')
def xkcd():
    return 'https://c.xkcd.com/random/comic'
