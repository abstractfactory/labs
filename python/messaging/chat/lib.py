import os
import argparse
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


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)

    def exit(self, status=0, message=None):
        raise SystemExit(message)
