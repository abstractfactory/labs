import flask
import flask.ext.restful
import flask.ext.restful.reqparse

import logging

app = flask.Flask(__name__)
api = flask.ext.restful.Api(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route("/")
def main():
    return "<h2>Hello World</h2>"


users = {
    "marcus": {"name": "Marcus",
               "age": 28,
               "address": "Home Street"},
    "peter": {"name": "Peter Liason",
              "age": 59,
              "address": "Gone street"}
}


class UserListApi(flask.ext.restful.Resource):
    """Create new user, or list existing users"""

    def __init__(self):
        super(UserListApi, self).__init__()

        parser = flask.ext.restful.reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True,
                            location="json", help="A name is required")
        parser.add_argument("age", type=int, required=True,
                            location="json", help="An age is required")

        self.parse_args = parser.parse_args

    def get(self):
        """Return existing users

        :status 200: All existing users

        :>header Content-Type: application/json

        :>jsonarr string name: Name of user
        :>jsonarr int age: Age of user

        """

        return users.values(), 200

    def post(self):
        """Create a new user

        :<json string name: Name of new user
        :<json int age: Age of new user

        :statuscode 201: Name of new user

        """

        args = self.parse_args()

        user = {
            "name": args["name"],
            "age": args["age"]
        }

        users[args["name"].lower()] = user
        return {"name": args["name"]}, 201


class UserApi(flask.ext.restful.Resource):
    def get(self, user_id):
        """Get specific user

        :param user_id: Unique id of user

        :>jsonarr string name: Name of user
        :>jsonarr string age: Age of user

        """

        try:
            data = users[user_id]
        except KeyError:
            return {"result": "No data for %s" % user_id}, 404
        return data, 200

    def put(self, user_id):
        """Update user at `user_id`

        :param user_id: Id of user

        :<json int age: New age of user
        :<json string favouriteColor: Users favourite color
        :<json string height: New user height
        :<json string weight: New user weight

        :>json int age: New age of user
        :>json string favouriteColor: Users favourite color (if exists)
        :>json string height: New user height (if exists)
        :>json string weight: New user weight (if exists)

        """

        if not user_id in users:
            return {"message": "User %s not found" % user_id}, 404

        parser = flask.ext.restful.reqparse.RequestParser()
        parser.add_argument("age", type=int, location="json")
        parser.add_argument("favouriteColor", type=str, location="json")
        parser.add_argument("height", type=str, location="json")
        parser.add_argument("weight", type=str, location="json")

        args = parser.parse_args()

        user = users[user_id]

        for arg, value in args.iteritems():
            if not value:
                continue
            user[arg] = value

        return user, 200

    def delete(self, user_id):
        success = False
        if user_id in users:
            users.pop(user_id)
            success = True

        return {"result": success}, 204


api.add_resource(UserListApi, "/app/v1.0/users", endpoint="users")
api.add_resource(UserApi, "/app/v1.0/users/<user_id>", endpoint="user")


if __name__ == '__main__':
    app.run(debug=True)
