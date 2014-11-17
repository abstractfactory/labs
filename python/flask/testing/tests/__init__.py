import os
import sys

tests_dir = os.path.dirname(__file__)
package_dir = os.path.dirname(tests_dir)

sys.path.insert(0, package_dir)

import server
server.app.config["TESTING"] = True
app = server.app.test_client()
app.testing = True
