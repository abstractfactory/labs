import threading


def spawn(func, **kwargs):
    thread = threading.Thread(target=func, **kwargs)
    thread.daemon = True
    thread.start()
