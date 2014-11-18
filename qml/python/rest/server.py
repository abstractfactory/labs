import flask
import logging

app = flask.Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route("/")
def main():
    return "<h2>Hello World</h2>"


people = {
    "marcus": {"name": "Marcus",
               "age": 28,
               "address": "Home Street"},
    "peter": {"name": "Peter Liason",
              "age": 59,
              "address": "Gone street"}
}


@app.route("/people", methods=["GET"])
def get_people():
    return flask.jsonify(result=people.values())


@app.route("/people", methods=["POST"])
def create_person():
    name = flask.request.json["name"]
    age = flask.request.json["age"]

    person = {
        "name": name,
        "age": age
    }

    people[name.lower()] = person
    return flask.jsonify(person), 201


@app.route("/people/<person>", methods=["PUT"])
def update_person(person):
    if not person in people:
        return 400

    person = people[person]
    person["age"] = flask.request.json.get("age", person["age"])
    return flask.jsonify(person)


@app.route("/people/<person>", methods=["DELETE"])
def delete_person(person):
    success = False
    if person in people:
        people.pop(person)
        success = True

    return flask.jsonify({"result": success})


@app.route("/people/<person>", methods=["GET"])
def get_person(person):
    try:
        data = people[person]
    except KeyError:
        return {"result": "No data for %s" % person}
    return flask.jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
