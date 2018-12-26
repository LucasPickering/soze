import os
from flask import Flask, jsonify, redirect, request

from .settings import Settings


app = Flask(__name__)
settings = Settings(os.environ["REDIS_DB"])


@app.before_first_request
def init_settings():
    settings.init_redis()


@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def route(path):
    try:
        if request.method == "GET":
            data = settings.get(path)
        elif request.method == "POST":
            data = settings.set(path, request.get_json())
    except KeyError as e:
        return jsonify(detail=f"Invalid setting: {str(e)}"), 404
    except ValueError as e:
        return jsonify(detail=str(e)), 400
    return jsonify(data)


@app.route("/xkcd")
def xkcd():
    return redirect("https://c.xkcd.com/random/comic")
