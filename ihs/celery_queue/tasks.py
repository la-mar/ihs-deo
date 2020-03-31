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

RETRY_BASE_DELAY = 15


@celery.task
def log(message):
    """Print some log messages"""
    logger.debug(message)
    logger.info(message)
    logger.warning(message)
    logger.error(message)
    logger.critical(message)


@celery.task
def smoke_test():
    """ Verify an arbitrary Celery task can run """
    return "verified"


@celery.task
def post_heartbeat():
    """ Send heartbeat to metrics backend"""
    return metrics.post_heartbeat()


@celery.task
def post_remote_export_capacity():
    """ Send remote export capacity to metrics backend"""
    calcs = collector.tasks.calc_remote_export_capacity()
    logger.debug("Posting metrics", extra=calcs)
    for key, value in calcs.items():
        metrics.post(key, value, metric_type="gauge")


@celery.task
def cleanup_remote_exports():
    """ Periodically checks the available export capacity on the IHS servers, purging
        completed exports if the used capacity >= ~1/3 of total export capacity. """
    calcs = collector.tasks.calc_remote_export_capacity()
    used = calcs.get("remote.capacity.used", 0)
    available = calcs.get("remote.capacity.available", 0)
    total = calcs.get("remote.capacity.total", 0)
    threshold = total * 0.33  # bytes

    if used >= threshold:
        logger.warning(
            f"Initiating remote purge: threshold={threshold}, capacity.used={used}, capacity.available={available}, capacity.total={total}"  # noqa
        )
        collector.tasks.purge_remote_exports()

        calcs_after = collector.tasks.calc_remote_export_capacity()
        used_after = calcs_after.get("remote.capacity.used", 0)
        available_after = calcs_after.get("remote.capacity.available", 0)
        total_after = calcs_after.get("remote.capacity.total", 0)
        threshold_after = total * 0.33  # bytes

        metrics.post_event(
            title="IHS Remote Export Purge",
            text=f"Completed Export Purge: (before) threshold={threshold}, capacity.used={used}, capacity.available={available}, capacity.total={total}"  # noqa
            + "\n"
            + f"(after) threshold={threshold_after}, capacity.used={used_after}, capacity.available={available_after}, capacity.total={total_after}",  # noqa
        )


@celery.task(rate_limit="10/s", ignore_result=True)
def sync_endpoint(endpoint_name: str, task_name: str, **kwargs) -> ExportJob:
    configs = list(collector.tasks.run_endpoint_task(endpoint_name, task_name))
    for idx, job_config in enumerate(configs):
        if job_config:
            logger.debug(f"Running task {endpoint_name}.{task_name}")
            hole_dir = job_config.get("metadata").get("hole_direction")
            countdown = 60 * (idx / count)
            submit_job.apply_async((hole_dir,), job_config, countdown=countdown)


@celery.task(bind=True, rate_limit="5/s", max_retries=0, ignore_result=True)
def submit_job(self, route_key: str, job_options: dict, metadata: dict = None):
    try:
        job = collector.tasks.submit_job(job_options, metadata or {})
        logger.debug(f"submitted job: {job}")
        if job:
            collect_job_result.apply_async(
                (route_key,), {"job": job.to_dict()}, countdown=60
            )
    except Exception as exc:
        logger.error(
            f"failed to submit job {job_options} (attempt: {self.request.retries}) -- {exc}",
            extra={"attempt": self.request.retries},
        )
        raise self.retry(exc=exc, countdown=RETRY_BASE_DELAY ** self.request.retries)


@celery.task(bind=True, rate_limit="100/s", max_retries=0, ignore_result=True)
def collect_job_result(self, route_key: str, job: Union[dict, ExportJob]):
    if not isinstance(job, ExportJob):
        job = ExportJob(**job)
    logger.debug(f"collecting job: {job}")
    try:
        collector.tasks.collect(job)

    except Exception as exc:
        logger.error(
            f"failed to collect job {job} (attempt: {self.request.retries}) -- {exc}",
            extra={"attempt": self.request.retries},
        )
        raise self.retry(exc=exc, countdown=RETRY_BASE_DELAY ** self.request.retries)


# @celery.task(bind=True, max_retries=0, ignore_result=True)
# def delete_job(self, route_key: str, job: Union[dict, ExportJob]):
#     if not isinstance(job, ExportJob):
#         job = ExportJob(**job)
#     logger.debug(f"deleting job: {job}")
#     try:
#         return collector.tasks.delete_job(job)
#     except Exception as exc:
#         logger.error(
#             f"failed to delete job {job} (attempt: {self.request.retries}) -- {exc}",
#             extra={"attempt": self.request.retries},
#         )
#         raise self.retry(exc=exc, countdown=RETRY_BASE_DELAY ** self.request.retries)


def process_changes_and_deletes():  # TODO: implement
    pass


if __name__ == "__main__":
    idx = list(range(1, 700 + 1))
    idx = [1, 10, 100, 300, 500, 600, 700]
    count = len(idx)
    count
    [(x, (x / count) ** 2) for x in idx]
    [(x, 60 * (x / count)) for x in idx]
