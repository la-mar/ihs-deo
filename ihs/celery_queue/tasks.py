from typing import Union

from celery.utils.log import get_task_logger

import collector.tasks
import metrics
from collector import Endpoint, ExportJob
from config import get_active_config
from ihs import celery

logger = get_task_logger(__name__)

conf = get_active_config()
endpoints = Endpoint.load_from_config(conf)


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
    """ Send heartbeat to metrics backend"""
    return metrics.post_heartbeat()


@celery.task
def post_remote_export_capacity():
    """ Send remote export capacity to metrics backend"""
    # logger.warning("post_remote_export_capacity")
    calcs = collector.tasks.calc_remote_export_capacity()
    logger.info("Posting metrics", extra=calcs)
    for key, value in calcs.items():
        metrics.post(key, value, metric_type="gauge")


@celery.task
def cleanup_remote_exports():
    """ Periodically checks the available export capacity on the IHS servers, purging completed exports if the
        used capacity >= ~1/3 of total export capacity. """
    calcs = collector.tasks.calc_remote_export_capacity()
    used = calcs.get("remote.capacity.used", 0)
    available = calcs.get("remote.capacity.available", 0)
    total = calcs.get("remote.capacity.total", 0)
    threshold = total * 0.33  # bytes

    if used >= threshold:
        logger.info(
            f"Initiating remote purge: threshold={threshold}, capacity.used={used}, capacity.available={available}, capacity.total={total}"
        )
        collector.tasks.purge_remote_exports()

        calcs_after = collector.tasks.calc_remote_export_capacity()
        used_after = calcs_after.get("remote.capacity.used", 0)
        available_after = calcs_after.get("remote.capacity.available", 0)
        total_after = calcs_after.get("remote.capacity.total", 0)
        threshold_after = total * 0.33  # bytes

        metrics.post_event(
            title="IHS Remote Export Purge",
            text=f"Completed Export Purge: (before) threshold={threshold}, capacity.used={used}, capacity.available={available}, capacity.total={total}"
            + "\n"
            + f"(after) threshold={threshold_after}, capacity.used={used_after}, capacity.available={available_after}, capacity.total={total_after}",
        )


# pylint: disable=unused-argument
@celery.task(rate_limit="10/s", ignore_result=True)
def sync_endpoint(endpoint_name: str, task_name: str, **kwargs) -> ExportJob:
    for job_config in collector.tasks.run_endpoint_task(endpoint_name, task_name):
        if job_config:
            submit_job.apply_async(
                (job_config.get("metadata").get("hole_direction"),), job_config
            )


@celery.task(bind=True, max_retries=0, ignore_result=True)
def submit_job(self, route_key: str, job_options: dict, metadata: dict = None):
    try:
        job = collector.tasks.submit_job(job_options, metadata or {})
        logger.info(f"Submitted job: {job}")
        if job:
            collect_job_result.apply_async((route_key,), {"job": job.to_dict()})
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery.task(bind=True, max_retries=0, ignore_result=True)
def collect_job_result(self, route_key: str, job: Union[dict, ExportJob]):
    if not isinstance(job, ExportJob):
        job = ExportJob(**job)
    logger.info(f"Collecting job: {job}")
    try:
        collector.tasks.collect(job)
        delete_job.apply_async((route_key,), {"job": job.to_dict()})

    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery.task(bind=True, max_retries=0, ignore_result=True)
def delete_job(self, route_key: str, job: Union[dict, ExportJob]):
    if not isinstance(job, ExportJob):
        job = ExportJob(**job)
    logger.info(f"Collecting job: {job}")
    try:
        return collector.tasks.delete_job(job)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


def process_changes_and_deletes():  # TODO: implement

    pass
