import json

from bottle import route, run, post, get, request, response

from thought_log.analyzer import analyze_text
from thought_log.models import Note


@route("/hello")
def hello():
    return "Hello world"


@route("/analyze", method="POST")
def analyze():
    data = request.json
    text = data["text"]
    num_labels = int(data.get("num_labels", 1))
    include_score = bool(data.get("include_score", False))
    analysis = analyze_text(text, num_labels, include_score)
    return analysis


@route("/notes", method="GET")
def get_notes():
    response.content_type = "application/json"
    return json.dumps(list(map(lambda n: n.to_dict(), Note.find())))


@route("/notes/<id:int>", method="GET")
def get_note(id):
    note = Note.find_one({"id": id})
    return note.to_dict()
 

def serve(host="localhost", port=8080, debug=True):
    run(host=host, port=port, debug=debug)
