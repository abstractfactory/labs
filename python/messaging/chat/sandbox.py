from __future__ import absolute_import

import lib

parser = lib.ArgumentParser()
parser.add_argument("name", help="Name of product")
parser.add_argument("--quantity", default=1)
parser.add_argument("--milk", default=False)
parser.add_argument("--size")
args = parser.parse_args()

print args