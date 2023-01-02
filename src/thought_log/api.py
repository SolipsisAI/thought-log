import json

from bottle import route, run, request, response

from thought_log.config import DEBUG
from thought_log.analyzer import analyze_text
from thought_log.importer import web
from thought_log.models import Note, Notebook
from thought_log.utils import get_filetype


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
    record = resource.insert(request_data)
    return record.to_dict()


@route("/<name>/<id:int>", method="PATCH")
def update_record(name, id):
    # Set id in request_data so we can find it
    resource = RESOURCES[name]
    request_data = request.json
    record = resource.update(request_data, id=id)
    return record.to_dict()


@route("/<name>/<id:int>", method="GET")
def get_record(name, id):
    resource = RESOURCES[name]
    record = resource.find_one({"id": id})
    embed = request.query.get("_embed", None)
    limit = request.query.get("limit", None)
    order_by = request.query.get("order_by", None)
    sort_by = request.query.get("sort_by", None)
    return record.to_dict(
        embed=embed,
        limit=int(limit) if limit else None,
        order_by=order_by,
        sort_by=sort_by,
    )


@route("/<name>/import", method="POST")
def import_record(name):
    upload = request.POST["file"]
    filetype = get_filetype(upload.raw_filename)

    # Import data
    result = web.import_data(upload.file, filetype=filetype)

    return {"filetype": filetype, "filename": upload.raw_filename, "result": result}


def serve(host: str = "localhost", port: int = 8080, debug: bool = DEBUG):
    run(host=host, port=port, debug=debug, reloader=debug)
