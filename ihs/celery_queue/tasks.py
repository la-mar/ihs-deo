from typing import Union, List, Dict
import math
import uuid
import logging

from celery.utils.log import get_task_logger

import collector.tasks
import metrics
from collector import Endpoint, ExportJob
from config import get_active_config
from ihs import celery


# logger = get_task_logger(__name__)
logger = logging.getLogger(__name__)

conf = get_active_config()
endpoints = Endpoint.load_from_config(conf)

RETRY_BASE_DELAY = 15


def spread_countdown(n: int, multiplier: int = 30) -> float:
    return math.log(n + 1) * multiplier + n


def submit_jobs_from_task_configs(
    configs: List[Dict], endpoint_name: str, task_name: str
):

    for idx, job_config in enumerate(configs):
        if job_config:
            # name = job_config["metadata"]["name"]
            # target_model = job_config["metadata"]["target_model"]
            hole_dir = job_config["metadata"]["hole_direction"]

            countdown = spread_countdown(idx)
            submit_job.apply_async((hole_dir,), job_config, countdown=countdown)


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
        completed exports if the used capacity >= ~1/2 of total export capacity. """
    calcs = collector.tasks.calc_remote_export_capacity()
    used = calcs.get("remote.capacity.used", 0)
    available = calcs.get("remote.capacity.available", 0)
    total = calcs.get("remote.capacity.total", 0)
    threshold = total * 0.5  # bytes

    if used >= threshold:
        logger.warning(
            f"Initiating remote purge: threshold={threshold}, capacity.used={used}, capacity.available={available}, capacity.total={total}"  # noqa
        )
        collector.tasks.purge_remote_exports()

        calcs_after = collector.tasks.calc_remote_export_capacity()
        used_after = calcs_after.get("remote.capacity.used", 0)
        available_after = calcs_after.get("remote.capacity.available", 0)
        total_after = calcs_after.get("remote.capacity.total", 0)
        threshold_after = total * 0.5  # bytes

        metrics.post_event(
            title="IHS Remote Export Purge",
            text=f"Completed Export Purge: (before) threshold={threshold}, capacity.used={used}, capacity.available={available}, capacity.total={total}"  # noqa
            + "\n"
            + f"(after) threshold={threshold_after}, capacity.used={used_after}, capacity.available={available_after}, capacity.total={total_after}",  # noqa
        )


@celery.task
def download_changes_and_deletes():
    download_count: int = collector.tasks.download_changes_and_deletes()
    metrics.post("changes_and_deletes.downloaded", download_count)


@celery.task
def synchronize_master_lists():
    collector.tasks.synchronize_master_lists()


@celery.task
def refresh_master_lists():
    for configs, endpoint_name, task_name in collector.tasks.refresh_master_lists():
        submit_jobs_from_task_configs(configs, endpoint_name, task_name)


@celery.task(rate_limit="10/s", ignore_result=True)
def sync_endpoint(endpoint_name: str, task_name: str, **kwargs):
    configs = list(collector.tasks.run_endpoint_task(endpoint_name, task_name))
    submit_jobs_from_task_configs(configs, endpoint_name, task_name)


@celery.task(bind=True, rate_limit="25/s", max_retries=0, ignore_result=True)
def submit_job(self, route_key: str, job_options: dict, metadata: dict):
    self.metadata = metadata
    target_model = metadata["target_model"]

    if conf.SIMULATE_EXPENSIVE_TASKS:
        opts = {**job_options, **(metadata or {})}
        job = ExportJob(job_id=uuid.uuid4().hex, **opts)
        logger.warning(f"(***SIMULATED***) submitted job: {job} {self.metadata}")
        collect_job_result.apply_async((route_key,), {"job": job.to_dict()})
        return None

    else:
        try:
            job = collector.tasks.submit_job(job_options, metadata or {})
            if job:
                job_dict = job.to_dict()
                logger.info(f"({target_model}) submitted {job}")
                collect_job_result.apply_async(
                    (route_key,), {"job": job_dict}, countdown=120,
                )
        except Exception as exc:
            logger.error(
                f"({target_model}) failed to submit job {job_options} (attempt: {self.request.retries}) -- {exc}",  # noqa
                extra={"attempt": self.request.retries},
            )
            raise self.retry(
                exc=exc, countdown=RETRY_BASE_DELAY ** self.request.retries
            )


@celery.task(bind=True, rate_limit="1000/s", max_retries=0, ignore_result=True)
def collect_job_result(self, route_key: str, job: Union[dict, ExportJob]):

    if not isinstance(job, ExportJob):
        job = ExportJob(**job)
    self.metadata = job.limited_dict()
    target_model = self.metadata["target_model"]

    if conf.SIMULATE_EXPENSIVE_TASKS:
        logger.warning(f"(***SIMULATED***) collected job: {job} {self.metadata}")
        return None

    else:
        try:
            collector.tasks.collect(job)
            logger.info(f"({target_model}) collected {job}")

        except Exception as exc:
            logger.error(
                f"({target_model}) failed to collect job {job} (attempt: {self.request.retries}) -- {exc}",
                extra={"attempt": self.request.retries},
            )
            raise self.retry(
                exc=exc, countdown=RETRY_BASE_DELAY ** self.request.retries
            )


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


# if __name__ == "__main__":
#     idx = list(range(1, 700 + 1))
#     idx = [1, 10, 100, 300, 500, 600, 700]
#     count = len(idx)
#     count
#     [(x, (x / count) ** 2) for x in idx]
#     [(x, 60 * (x / count)) for x in idx]

#     import pandas as pd
#     import numpy as np

#     df = pd.DataFrame(data={"ct": range(0, 10000)})
#     df["log"] = df.ct.apply(np.log)
#     df["logx60"] = df.log.mul(60)
#     df["log+ctx60"] = df.log.mul(60).add(df.ct)
#     df["log+ctx30"] = df.log.mul(30).add(df.ct)
#     df = df.replace([-np.inf, np.inf], np.nan)
#     df.describe()
#     df["log+ctx30"].div(60).describe()
#     import math

#     math.log(10000)
