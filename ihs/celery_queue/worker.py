from __future__ import annotations

import logging

from celery import Celery
from celery.signals import after_setup_logger  # after_setup_task_logger
from celery.app.log import TaskFormatter

import loggers
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
                logger.warning("Registering periodic task: %s", name)
                sender.add_periodic_task(
                    task.schedule,
                    celery_queue.tasks.sync_endpoint.s(endpoint_name, task_name),
                    name=name,
                )
            else:
                logger.warning("Task %s is DISABLED -- skipping", name)
    sender.add_periodic_task(
        30, celery_queue.tasks.post_heartbeat, name="heartbeat",
    )


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):  # pylint: disable=unused-argument
    logger.setLevel(loggers.mlevel(conf.LOG_LEVEL))
    console_handler = loggers.ColorizingStreamHandler()
    console_handler.setFormatter(loggers.DatadogJSONFormatter())
    if logger.handlers:
        logger.removeHandler(logger.handlers[0])
    logger.addHandler(console_handler)


# @after_setup_task_logger.connect
# def setup_task_logger(logger, *args, **kwargs):
#     for handler in logger.handlers:
#         handler.setFormatter(
#             TaskFormatter(
#                 "%(asctime)s - %(task_id)s - %(task_name)s - %(name)s - %(levelname)s - %(message)s"
#             )
#         )


if __name__ == "__main__":
    print("test")
