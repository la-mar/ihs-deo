from __future__ import annotations
from typing import Optional, Dict
import logging

from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger, after_setup_task_logger

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
        metadata: Optional[Dict] = None

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
    if conf.CELERYBEAT_LOAD_ENDPOINTS:
        for endpoint_name, endpoint in endpoints.items():
            for task_name, task in endpoint.tasks.items():
                name = f"{endpoint_name}:{task_name}"
                if task.enabled:
                    logger.info("Registering periodic task: %s", name)
                    sender.add_periodic_task(
                        task.schedule,
                        celery_queue.tasks.sync_endpoint.s(endpoint_name, task_name),
                        name=name,
                    )
                else:
                    logger.warning("Task %s is DISABLED -- skipping", name)
    else:
        logger.warning(
            "Endpoint tasks are DISABLED. Set CELERYBEAT_LOAD_ENDPOINTS=True to enable."
        )

    # logger.info("Registering periodic task: %s", "heartbeat")
    # sender.add_periodic_task(
    #     30, celery_queue.tasks.post_heartbeat.s(), name="heartbeat",
    # )

    logger.info("Registering periodic task: %s", "calc_remote_export_capacity")
    sender.add_periodic_task(
        60,  # seconds
        celery_queue.tasks.post_remote_export_capacity.s(),
        name="calc_remote_export_capacity",
    )

    # logger.info("Registering periodic task: %s", "cleanup_remote_exports")

    # sender.add_periodic_task(
    #     crontab(
    #         minute=0, hour=0
    #     ),  # daily at midnight, ~3 hours before nightly jobs start
    #     celery_queue.tasks.cleanup_remote_exports,
    #     name="cleanup_remote_exports",
    # )

    logger.info("Registering periodic task: %s", "download_changes_and_deletes")
    sender.add_periodic_task(
        crontab(minute=0, hour=15),
        celery_queue.tasks.download_changes_and_deletes.s(),
        name="download_changes_and_deletes",
    )

    # logger.info("Registering periodic task: %s", "refresh_master_lists")
    # sender.add_periodic_task(
    #     crontab(minute=50, hour=19),
    #     celery_queue.tasks.refresh_master_lists,
    #     name="refresh_master_lists",
    # )

    logger.info("Registering periodic task: %s", "synchronize_master_lists")
    sender.add_periodic_task(
        crontab(minute=50, hour="*/3"),
        celery_queue.tasks.synchronize_master_lists.s(),
        name="synchronize_master_lists",
    )


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    """ Configure the root logger on worker/beat startup """
    loggers.config(
        logger=logger, level=conf.CELERY_LOG_LEVEL, formatter=conf.CELERY_LOG_FORMAT
    )


@after_setup_task_logger.connect
def setup_task_loggers(logger, *args, **kwargs):
    """ Configure loggers on worker/beat startup """
    loggers.config(logger=logger, level=conf.LOG_LEVEL, formatter=conf.LOG_FORMAT)


# @after_setup_logger.connect
# def setup_loggers(logger, *args, **kwargs):  # pylint: disable=unused-argument
#     loggers.config(logger=logger)


if __name__ == "__main__":
    print("test")

    dir(celery.Task)
