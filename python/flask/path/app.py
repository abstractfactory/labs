import flask

app = flask.Flask(__name__)


@app.route("/")
def main(something=None):
    with open("templates/index.html") as f:
        content = f.read()
    return flask.make_response(content)


if __name__ == '__main__':
    app.run(debug=True)
