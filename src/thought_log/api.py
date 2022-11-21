from bottle import route, run, post, request

from thought_log.analyzer import analyze_text


@route("/hello")
def hello():
    return "Hello world"


@post("/analyze")
def analyze():
    data = request.json
    text = data["text"]
    num_labels = data.get("num_labels", 1)
    include_score = data.get("include_score", False)
    analysis = analyze_text(text, num_labels, include_score)
    return analysis


def serve(host="localhost", port=8080, debug=True):
    run(host=host, port=port, debug=debug)
