import os
import redis
from flask import Flask, jsonify, redirect, request

from . import logger
from .error import SozeError
from .resource import Led, Lcd


app = Flask(__name__)
# This will NOT initiate a connection to Redis yet
redis_client = redis.from_url(os.environ["REDIS_HOST"])
resources = {res.name: res for res in [Led(redis_client), Lcd(redis_client)]}


@app.before_first_request
def init_settings():
    # Initialize Redis for each resource. This will insert any missing keys.
    logger.info("Initializing Redis data...")
    for resource in resources.values():
        resource.init_redis()
    logger.info("Redis initialized")


# One route handles GET/POST for all resources
@app.route(f"/<resource_name>", methods=["GET", "POST"])
def resource_route(resource_name):
    try:
        resource = resources[resource_name]
    except KeyError:
        return jsonify(detail=f"Unknown resource: {resource_name}"), 404
    if request.method == "GET":
        data = resource.get()
    elif request.method == "POST":
        try:
            data = resource.update(request.get_json())
        except SozeError as e:
            return jsonify(detail=str(e)), 400
    return jsonify(data)


@app.route("/xkcd")
def xkcd():
    return redirect("https://c.xkcd.com/random/comic")
