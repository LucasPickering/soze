import os
import redis
from flask import Flask, jsonify, redirect, request, abort, make_response

from . import logger
from .error import SozeError
from .resource import Led, Lcd, STATUSES


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


def validate_resource(resource_name):
    """
    Validates the given resource name. If it's valid, returns the resource
    object. If not, aborts the request with a 404
    """
    try:
        return resources[resource_name]
    except KeyError:
        abort(
            make_response(
                jsonify(message=f"Unknown resource: {resource_name}"), 404
            )
        )


def validate_status(status):
    """
    Validates the given status. If it's valid, returns None. If not, aborts the
    request with a 404.
    """
    if status not in STATUSES:
        abort(make_response(jsonify(message=f"Unknown status: {status}"), 404))


# Get all statuses for a resource
@app.route(f"/<resource_name>", methods=["GET"])
def resource_route(resource_name):
    resource = validate_resource(resource_name)

    # Get data for all statuses, and put them in a dict
    data = {status: resource.get(status) for status in STATUSES}
    return jsonify(data)


# One route handles GET/POST for all resource/status pairs
@app.route(f"/<resource_name>/<status>", methods=["GET", "POST"])
def resource_status_route(resource_name, status):
    resource = validate_resource(resource_name)
    validate_status(status)  # Check that it's a valid status

    if request.method == "GET":
        data = resource.get(status)
    elif request.method == "POST":
        try:
            data = resource.update(status, request.get_json())
        except SozeError as e:
            return jsonify(detail=str(e)), 400
    return jsonify(data)


@app.route("/xkcd")
def xkcd():
    return redirect("https://c.xkcd.com/random/comic")
