from __future__ import annotations

import logging

from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger  # after_setup_task_logger

import celery_queue.tasks
import loggers
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

    class ContextTask(TaskBase):  # noqa
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
                logger.debug("Registering periodic task: %s", name)
                sender.add_periodic_task(
                    task.schedule,
                    celery_queue.tasks.sync_endpoint.s(endpoint_name, task_name),
                    name=name,
                )
            else:
                logger.warning("Task %s is DISABLED -- skipping", name)

    logger.debug("Registering periodic task: %s", "heartbeat")
    sender.add_periodic_task(
        30, celery_queue.tasks.post_heartbeat, name="heartbeat",
    )

    logger.debug("Registering periodic task: %s", "calc_remote_export_capacity")
    sender.add_periodic_task(
        60,  # 1 minute
        celery_queue.tasks.post_remote_export_capacity,
        name="calc_remote_export_capacity",
    )

    logger.debug("Registering periodic task: %s", "cleanup_remote_exports")
    sender.add_periodic_task(
        crontab(
            minute=0, hour=0
        ),  # daily at midnight, ~3 hours before nightly jobs start
        celery_queue.tasks.cleanup_remote_exports,
        name="cleanup_remote_exports",
    )

    sender.add_periodic_task(
        crontab(minute=0, hour=15),
        celery_queue.tasks.download_changes_and_deletes,
        name="download_changes_and_deletes",
    )


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    """ Configure loggers on worker/beat startup """
    loggers.config(
        logger=logger, level=conf.CELERY_LOG_LEVEL, formatter=conf.CELERY_LOG_FORMAT
    )


# @after_setup_logger.connect
# def setup_loggers(logger, *args, **kwargs):  # pylint: disable=unused-argument
#     loggers.config(logger=logger)


if __name__ == "__main__":
    print("test")
