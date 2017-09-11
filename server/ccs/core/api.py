from flask import json, request

from ccs import app
from .color import Color
from . import settings


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Color):
            return obj.to_list()
        return obj


def _to_json(data):
    if 'pretty' in request.args:
        return json.dumps(data, cls=Encoder, indent=4) + '\n'
    return json.dumps(data, cls=Encoder)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def route(path):
    if request.method == 'GET':
        data = settings.get(path)
        return _to_json(data)
    elif request.method == 'POST':
        data = settings.set(path, request.get_json())
        return _to_json(data)


@app.route('/xkcd')
def xkcd():
    return 'https://c.xkcd.com/random/comic'
