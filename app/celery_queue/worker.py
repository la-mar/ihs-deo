from __future__ import annotations

import logging
from typing import List, Union

from celery import Celery
from celery.schedules import crontab

import collector.endpoint
from collector.tasks import post_heartbeat, sync_endpoint
from config import get_active_config
from app import create_app

logger = logging.getLogger(__name__)

conf = get_active_config()


def create_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["BROKER_URL"],
        include=app.config["CELERY_TASK_LIST"],
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):  # pylint: disable=inherit-non-class
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


flask_app = create_app()
celery = create_celery(flask_app)


class Task:
    """ A yaml defined task object to be passed to Celery """

    def __init__(
        self,
        model_name: str,
        task_name: str,
        cron: dict = None,
        seconds: int = None,
        mode: str = None,
        options: dict = None,
        enabled: bool = True,
        **kwargs,
    ):
        self.model_name = model_name
        self.task_name = task_name
        self.cron = self.parse_cron(cron or {})
        self.seconds = seconds
        self.mode = mode
        self.options = options or {}
        self.enabled = enabled

        if not any([self.cron, self.seconds]):
            raise ValueError("Either seconds or cron must be specified")

    def __repr__(self):
        status = "***DISABLED***" if not self.enabled else ""
        s = self.schedule
        sch = (
            f"{s._orig_minute} {s._orig_hour} {s._orig_day_of_week} {s._orig_day_of_month} {s._orig_month_of_year}"
            if self.seconds is None
            else f"({self.schedule} seconds)"
        )
        opts = ", ".join([f"{k}:{v}" for k, v in self.options.items()])
        return f"{status} {self.qualified_name} {sch} {opts}"

    @property
    def qualified_name(self):
        return f"{self.model_name}/{self.task_name}"

    @property
    def schedule(self) -> Union[crontab, int]:
        """ The scheduling expression to be used for task creation. Prefers seconds over cron expressions. """
        return self.seconds or self.cron

    @staticmethod
    def parse_cron(cron: dict):
        """ Return a crontab object if the passed dict has any non-null values """
        notnull = {k: v for k, v in cron.items() if v is not None}
        if len(notnull) > 0:
            return crontab(**notnull)
        else:
            return None


def tasks_from_app_config(conf: object):
    """ Retrieves collection task definitions from the active configuration and parses
    them into Task objects """
    for_scheduling: List[Task] = []
    endpoints = collector.endpoint.load_from_config(conf, load_disabled=False)
    for model_name, _ in endpoints.items():  # type: ignore
        tasks = conf.endpoints.get(model_name).get("tasks", {})  # type: ignore
        for task_name, task_def in tasks.items():
            try:
                # for name, schedule in task_defs.items():
                print(f"Attempting to create task for: {model_name}")
                new = Task(model_name, task_name, **task_def)
                for_scheduling.append(new)
                print(f"Created Task {new}")
            except ValueError as ve:
                logger.error(
                    f"Failed to create scheduled task ({model_name}/{task_name}) -- {ve}"
                )

    return for_scheduling


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """ Schedules a periodic task for each configured collection task """
    tasks = tasks_from_app_config(conf)
    for task in tasks:
        if task.enabled:
            add_periodic_task(
                sender, name=task.model_name, mode=task.mode, **task.options
            )
        else:
            print(f"{task} is disabled. Skipping execution.")

    sender.add_periodic_task(
        30, post_heartbeat, name="heartbeat",
    )


def add_periodic_task(
    sender, name: str, schedule: Union[crontab, int], *args, **kwargs
):
    sender.add_periodic_task(
        schedule, sync_endpoint.s(*args, **kwargs), name=name,
    )


def get_celery_queue_items(queue_name):
    import base64
    import json
    import pickle

    with celery.pool.acquire(block=True) as conn:
        tasks = conn.default_channel.client.lrange(queue_name, 0, -1)
        decoded_tasks = []

    for task in tasks:
        j = json.loads(task)
        # body = json.loads(base64.b64decode(j["body"]))
        body = pickle.loads(base64.b64decode(j["body"]))
        decoded_tasks.append(body)

    return decoded_tasks


if __name__ == "__main__":
    endpoints = collector.endpoint.load_from_config(conf)
    ep = endpoints["production"]
    model = ep.model
    tasks = tasks_from_app_config(conf)
    tasks
    [t.enabled for t in tasks]
    [e.enabled for e in endpoints.values()]

    get_celery_queue_items("default")
