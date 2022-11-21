from bottle import route, run, post, request

from thought_log.analyzer import analyze_text


@route("/hello")
def hello():
    return "Hello world"


@post("/analyze")
def analyze():
    data = request.json
    text = data["text"]
    averaged = data.get("averaged", False)
    analysis = analyze_text(text, averaged)
    return analysis


def serve(host='localhost', port=8080, debug=True):
    run(host=host, port=port, debug=debug)
