"""Simple flask server

The only reason we are not using:

```python
$ python -m SimpleHTTPServer
```

Is due to the use of ngRoute which needs to serve an identical
html file for every address; thus the wild-card <path:p> you
see below.

"""

import flask

app = flask.Flask(__name__)


@app.route("/", defaults={"p": ""})
@app.route("/<path:p>")
def index(p):
    with open("static/index.html") as f:
        content = f.read()
    return flask.make_response(content)


if __name__ == "__main__":
    app.run(debug=True)
