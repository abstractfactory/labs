import os
import threading
import subprocess


def spawn(func, **kwargs):
    thread = threading.Thread(target=func, **kwargs)
    thread.daemon = True
    thread.start()


clear_console = lambda: subprocess.call(
    'cls'
    if os.name == 'nt'
    else 'clear',
    shell=True)
