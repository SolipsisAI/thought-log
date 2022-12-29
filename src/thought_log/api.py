import json

from bottle import route, run, request, response

from thought_log.analyzer import analyze_text
from thought_log.models import Note, Notebook


RESOURCES = {"notes": Note, "notebooks": Notebook}


@route("/analyze", method="POST")
def analyze():
    data = request.json
    text = data["text"]
    num_labels = int(data.get("num_labels", 1))
    include_score = bool(data.get("include_score", False))
    analysis = analyze_text(text, num_labels, include_score)
    return analysis


@route("/<name>", method="GET")
def get_record_list(name):
    response.content_type = "application/json"
    return json.dumps(list(map(lambda n: n.to_dict(), RESOURCES[name].find())))


@route("/<name>", method="POST")
def post_record(name):
    request_data = request.json
    resource = RESOURCES[name]
    resource.upsert(request_data)
    return resource.last().to_dict()


@route("/<name>/<id:int>", method="GET")
def get_record(name, id):
    resource = RESOURCES[name]
    record = resource.find_one({"id": id})
    return record.to_dict()


@route("/<name>/<id:int>", method="PATCH")
def update_note(name, id):
    request_data = request.json
    # Set id in request_data so we can find it
    request_data["id"] = id
    resource = RESOURCES[name]
    resource.upsert(request_data)
    record = resource.find_one({"id": id})
    return record.to_dict()


def serve(host="localhost", port=8080, debug=True):
    run(host=host, port=port, debug=debug, reloader=debug)
