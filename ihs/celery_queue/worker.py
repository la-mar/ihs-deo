from __future__ import annotations

import logging

from celery import Celery

import celery_queue.tasks
from collector import Endpoint
from config import get_active_config
from ihs import create_app

logger = logging.getLogger(__name__)

conf = get_active_config()
endpoints = Endpoint.load_from_config(conf)


def create_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["BROKER_URL"],
        include=app.config["CELERY_TASK_LIST"],
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


flask_app = create_app()
celery = create_celery(flask_app)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):  # pylint: disable=unused-argument
    """ Schedules a periodic task for each configured endpoint task """
    for endpoint_name, endpoint in endpoints.items():
        for task_name, task in endpoint.tasks.items():
            if task.enabled:
                name = f"{endpoint_name}:{task_name}"
                logger.info("Registering periodic task: %s", name)
                sender.add_periodic_task(
                    task.schedule,
                    celery_queue.tasks.sync_endpoint.s(endpoint_name, task_name),
                    name=name,
                )
            else:
                logger.info("Task %s is disabled -- skipping", name)
    sender.add_periodic_task(
        30, celery_queue.tasks.post_heartbeat, name="heartbeat",
    )


if __name__ == "__main__":
    endpoint = endpoints["wells"]
