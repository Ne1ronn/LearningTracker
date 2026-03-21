import os
from celery import Celery

app = Celery("tasks")
app.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
app.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")


@app.task
def add(x, y):
    return x + y
