from celery import Celery

app = Celery('tasks', broker='amqp://localhost//')


@app.task
def add(x, y):
    return x + y
