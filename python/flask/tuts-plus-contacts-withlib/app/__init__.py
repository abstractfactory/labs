import flask
import flask.ext.restful

from .api import ApiContact, ApiContactId


app = flask.Flask(__name__)
api = flask.ext.restful.Api(app)

api.add_resource(ApiContact, '/api/contact')
api.add_resource(ApiContactId, '/api/contact/<string:id>')


from .routes import index
