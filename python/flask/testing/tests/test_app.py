import json
from nose.tools import *

from tests import app


def test_app():
    response = app.get("/people")
    eq_(response.headers["Content-Type"], "application/json")
    eq_(response.status_code, 200)

    response = app.post("/people",
                        data={"color": "brown",
                              "person": "marcus"})
    eq_(response.status_code, 200)
    data = json.loads(response.data)
    assert data == 2, data
