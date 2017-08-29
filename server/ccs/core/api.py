from flask import json, request

from ccs import app, logger
from .settings import Settings

_SETTINGS = Settings()


def to_json(data):
    if 'pretty' in request.args:
        return json.dumps(data, indent=4) + '\n'
    return json.dumps(data)


@app.route('/', defaults={'path': ''})
@app.route('/<path>', methods=['GET', 'POST'])
def route(path):
    if request.method == 'GET':
        return to_json(_SETTINGS.get(path))
    elif request.method == 'POST':
        for k, v in request.get_json().items():
            _SETTINGS.set(path + k, v)
        return to_json(_SETTINGS.get(path))


@app.route('/xkcd')
def xkcd():
    return 'https://c.xkcd.com/random/comic'
