from typing import Union

from celery.utils.log import get_task_logger

import collector.tasks
from collector import Endpoint, ExportJob
from config import get_active_config
from ihs import celery

logger = get_task_logger(__name__)

conf = get_active_config()
endpoints = Endpoint.load_from_config(conf)


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ["Starting up", "Booting", "Repairing", "Loading", "Checking"]
    adjective = ["master", "radiant", "silent", "harmonic", "fast"]
    noun = ["solar array", "particle reshaper", "cosmic ray", "orbiter", "bit"]
    message = ""
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = "{0} {1} {2}...".format(
                random.choice(verb), random.choice(adjective), random.choice(noun)
            )
        self.update_state(
            state="PROGRESS", meta={"current": i, "total": total, "status": message}
        )
        time.sleep(1)
    return {"current": 100, "total": 100, "status": "Task completed!", "result": 42}


@celery.task
def log(message):
    """Print some log messages"""
    logger.debug(message)
    logger.info(message)
    logger.warning(message)
    logger.error(message)
    logger.critical(message)


@celery.task
def post_heartbeat():
    """ Sync model from source to data warehouse"""
    return metrics.send(f"{project}.heartbeat", 1)


@celery.task(bind=True, max_retries=0, ignore_result=True)
def collect_job_result(self, job: Union[dict, ExportJob]):
    if not isinstance(job, ExportJob):
        job = ExportJob(**job)
    logger.info(f"Collecting job: {job}")
    try:
        return collector.tasks.collect(job)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery.task(bind=True, max_retries=0, ignore_result=True)
def submit_job(self, job_options: dict, metadata: dict = None):
    try:
        job = collector.tasks.submit_job(job_options, metadata or {})
        logger.info(f"Submitted job: {job}")
        if job:
            collect_job_result.apply_async((), {"job": job.to_dict()})
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


# pylint: disable=unused-argument
@celery.task(rate_limit="10/s", ignore_result=True)
def sync_endpoint(endpoint_name: str, task_name: str, **kwargs) -> ExportJob:
    for job_config in collector.tasks.run_endpoint_task(endpoint_name, task_name):
        if job_config:
            submit_job.apply_async((), job_config)
