from flask import Flask, json, redirect, request

from . import settings


app = Flask(__name__)


def to_json(data):
    if "pretty" in request.args:
        return json.dumps(data, indent=4) + "\n"
    return json.dumps(data)


@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def route(path):
    try:
        if request.method == "GET":
            data = settings.get(path, serialized=True)
        elif request.method == "POST":
            data = settings.set(path, request.get_json())
    except (KeyError, ValueError) as e:
        return to_json({"detail": str(e)}), 400
    return to_json(data)


@app.route("/xkcd")
def xkcd():
    return redirect("https://c.xkcd.com/random/comic")
