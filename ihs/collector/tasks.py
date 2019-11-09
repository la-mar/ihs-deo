from __future__ import annotations
from typing import List, Dict, Tuple
import random
import time
from datetime import datetime, timedelta

from celery.signals import task_postrun, setup_logging
from celery.utils.log import get_task_logger
from flask_sqlalchemy import Model


# it is important that this celery instance is t`he same as the primary flask app and NOT a new instance from celery_worker.py
from app import celery, db, create_app
from api.models import *
from collector.collector import IWellCollector
from collector.endpoint import load_from_config
from collector.requestor import IWellRequestor
from collector.request import Request
from collector.endpoint import Endpoint
from config import get_active_config, project
import metrics

conf = get_active_config()
endpoints = load_from_config(conf)


logger = get_task_logger(__name__)


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


@celery.task(bind=True, max_retries=2, ignore_result=True)
def collect_request(self, request: Request, endpoint: Endpoint):
    try:
        return _collect_request(request, endpoint)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


def _collect_request(request: Request, endpoint: Endpoint):
    c = IWellCollector(endpoint)
    logger.info(f"Collecting {request}")
    response = request.get()
    # logger.warning(response)
    if not response.ok:
        if response.status_code == 404:
            logger.info(f"{request}: Resource not found")
        else:
            raise Exception(
                f"GET {response.url} returned unexpected response code: {response.status_code}"
            )
    result = c.collect(response)
    capture_result(endpoint, result)
    post_metric(endpoint, result)
    return result


@celery.task(bind=True, rate_limit="100/s", ignore_result=True)
def sync_endpoint(self, endpoint_name: str, **kwargs):
    return _sync_endpoint(endpoint_name, celery=True, **kwargs)


def _sync_endpoint(endpoint_name: str, celery: bool = False, **kwargs):
    """ Sync model from source to backend"""
    endpoint = endpoints[endpoint_name]
    requestor = IWellRequestor(conf.API_BASE_URL, endpoint, **kwargs)
    errors: List[str] = []
    if endpoint.enabled:
        for req in requestor.sync_model():
            logger.debug(f"Sending request to {req}")
            try:
                if celery:
                    result = collect_request.apply_async((req, endpoint))
                else:
                    result = _collect_request(req, endpoint)

            except Exception as e:
                logger.warning(f"Unable to collect request: {req}")
                errors.append(f"{req}: {e}")

        if len(errors) > 0:
            err = "\n".join(errors)
            logger.error(
                f"Captured {len(errors)} errors when syncing endpoint: "
                + "\n"
                + f"{err}"
            )
    else:
        logger.info(f"{endpoint} is disabled. Skipping execution.")


def capture_result(endpoint: Endpoint, result: dict) -> None:
    logger.debug(f"capturing results: {endpoint}: {len(result.keys())}")
    if len(result.keys()) > 0:
        result.update(
            {
                "integrated_at": datetime.now(),
                "model_name": f"{endpoint.model.__module__}.{endpoint.model.__tablename__}",
            }
        )
        IntegrationLog.s.add(IntegrationLog(**result))  # type: ignore
        IntegrationLog.persist()  # type: ignore


def post_metric(endpoint: Endpoint, result: dict) -> None:
    for k, v in result.items():
        try:
            name = f"{project}.{endpoint.name}.{k}"
            points = v
            metrics.send(name, points)
        except Exception as e:
            logger.debug(
                "Failed to post metric: name=%s, points=%s, error=%s", name, points, e
            )


@task_postrun.connect
def close_session(*args, **kwargs):
    # Flask SQLAlchemy will automatically create new sessions for you from
    # a scoped session factory, given that we are maintaining the same app
    # context, this ensures tasks have a fresh session (e.g. session errors
    # won't propagate across tasks)
    db.session.remove()


# from celery.task import Task
# from collector.requestor import Requestor
# from collector.endpoint import Endpoint


# class SyncModel(Task):
#     def run(self, **kwargs):
#         print("SyncModelTask")


if __name__ == "__main__":
    import logging

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    endpoint_name = "users"
    app = create_app()
    app.app_context().push()
