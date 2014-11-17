import flask
import flask.ext.restful
import flask.ext.restful.reqparse

app = flask.Flask(__name__)
api = flask.ext.restful.Api(app)


parser = flask.ext.restful.reqparse.RequestParser()
parser.add_argument('color',
                    type=str,
                    required=True)
parser.add_argument('pekson',
                    type=str,
                    required=True)


class People(flask.ext.restful.Resource):
    def get(self):
        return {"message": "Complete"}

    def post(self):

        args = parser.parse_args()

        return {
            "id": "1234",
            "person": args["person"],
            "color": args["color"]
        }


api.add_resource(People, "/people")
