import os
import sys
import subprocess

args = sys.argv

path, ext = os.path.splitext(args.pop(0))

script = path + ".py"
python = 'python'

if not os.path.isfile(script):
    script = path + ".pyw"
    python = 'pythonw'

if not os.path.isfile(script):
    return sys.stderr.write("No script matching the filename: %s" % path)

subprocess.Popen([python, script] + sys.argv[1:])
