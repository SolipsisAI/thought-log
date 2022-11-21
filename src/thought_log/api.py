from bottle import route, run


@route("/hello")
def hello():
    return "Hello world"


def serve(host='localhost', port=8080, debug=True):
    run(host=host, port=port, debug=debug)
