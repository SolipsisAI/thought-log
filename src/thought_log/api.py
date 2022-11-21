from bottle import route, run, post, request

from thought_log.analyzer import analyze_text


@route("/hello")
def hello():
    return "Hello world"


@post("/analyze")
def analyze():
    data = request.json
    text = data["text"]
    analysis = analyze_text(text)
    return analysis


def serve(host='localhost', port=8080, debug=True):
    run(host=host, port=port, debug=debug)
