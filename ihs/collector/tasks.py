from __future__ import annotations
from typing import Union, Generator
import logging


from ihs import create_app
from api.models import *  # noqa
from collector import (  # noqa
    XMLParser,
    Endpoint,
    ExportParameter,
    ExportBuilder,
    ExportJob,
    ExportRetriever,
    WellboreTransformer,
    ProductionTransformer,
    WellList,
    ProductionList,
)
from collector.identity_list import IdentityList
from collector.collector import Collector
from config import get_active_config, project, IdentityTemplates, ExportDataTypes
import metrics

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
conf = get_active_config()
endpoints = Endpoint.load_from_config(conf)


def run_endpoint_task(
    endpoint_name: str, task_name: str
) -> Generator[dict, None, None]:
    """ Unpack task options and assemble metadata for job configuration """
    endpoint = endpoints[endpoint_name]
    task = endpoint.tasks[task_name]
    for opts in task.options:
        yield dict(
            job_options=opts,
            metadata={
                "endpoint": endpoint_name,
                "task": task_name,
                "url": conf.API_BASE_URL,
                "hole_direction": opts.get("criteria", {}).get("hole_direction"),
                **opts,  # duplicate job options here to they travel with the job throughout its lifecycle
            },
        )


def submit_job(job_options: dict, metadata: dict) -> ExportJob:
    endpoint_name = metadata.get("endpoint")
    endpoint = endpoints[endpoint_name]
    ep = ExportParameter(**job_options)
    requestor = ExportBuilder(endpoint)
    return requestor.submit(ep, metadata=metadata or {})


def collect(job: Union[dict, ExportJob]):
    if isinstance(job, dict):
        job = ExportJob(**job)

    isIdentityExport = IdentityTemplates.has_member(job.template)
    data = get_job_results(job)

    if isIdentityExport:
        collect_identities(job, data)
    else:
        collect_data(job, data)


def get_job_results(job: Union[ExportJob, dict]) -> bytes:
    if not isinstance(job, ExportJob):
        job = ExportJob(**job)
    # logger.info(f"Fetching job results: {job}")
    retr = ExportRetriever(job, base_url=job.url, endpoint=endpoints[job.endpoint])
    data = retr.get()
    return data


def collect_data(job: ExportJob, xml: bytes):
    if xml:
        parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
        document = parser.parse(xml)
        collector = Collector(endpoints[job.endpoint].model)
        if job.data_type == ExportDataTypes.WELL.value:
            data = WellboreTransformer.extract_from_collection(document)
        elif job.data_type == ExportDataTypes.PRODUCTION.value:
            data = ProductionTransformer.extract_from_collection(document)
        collector.save(data)


def collect_identities(job: ExportJob, data: bytes) -> IdentityList:
    interface = None
    if job.data_type == ExportDataTypes.WELL.value:
        interface = WellList(job.name, job.criteria.get("hole_direction"))
        interface.ids = data
    elif job.data_type == ExportDataTypes.PRODUCTION.value:
        interface = ProductionList(job.name, job.criteria.get("hole_direction"))
        interface.ids = data

    return interface


def delete_job(job: ExportJob) -> bool:
    endpoint = endpoints[job.endpoint]
    requestor = ExportBuilder(endpoint)
    result = False
    if requestor.job_exists(job):
        result = requestor.delete_job(job)
    return result


def post_metric(endpoint: Endpoint, result: dict):
    for k, v in result.items():
        try:
            name = f"{project}.{endpoint.name}.{k}"
            points = v
            metrics.send(name, points)
        except Exception as e:
            logger.debug(
                "Failed to post metric: name=%s, points=%s, error=%s", name, points, e
            )


if __name__ == "__main__":
    # pylint: disable-all

    from ihs import create_app

    logging.basicConfig(level=20)
    app = create_app()
    app.app_context().push()

    endpoint_name = "production_horizontal"
    task_name = "sequoia"
    results = [x for x in run_endpoint_task(endpoint_name, task_name) if x is not None]
    opts = results[0]
    opts.get("job_options")
    job = submit_job(**opts)
    dir(job)
    job.to_dict()
    result = get_job_results(job)
    collect_data(job, result)

    endpoint_name = "well_horizontal"
    task_name = "sequoia"
    results = [x for x in run_endpoint_task(endpoint_name, task_name) if x is not None]
    opts = results[0]
    opts.get("job_options")
    job = submit_job(**opts)
    dir(job)
    job.to_dict()
    result = get_job_results(job)
    collect_data(job, result)

    endpoint_name = "production_master_horizontal"
    task_name = "sync"
    results = [x for x in run_endpoint_task(endpoint_name, task_name) if x is not None]
    opts = results[0]
    opts.get("job_options")
    job = submit_job(**opts)
    dir(job)
    job.to_dict()
    result = get_job_results(job)
    collect_identities(job, result)

    endpoint_name = "well_master_horizontal"
    task_name = "sync"
    results = [x for x in run_endpoint_task(endpoint_name, task_name) if x is not None]
    opts = results[0]
    opts.get("job_options")
    job = submit_job(**opts)
    dir(job)
    job.to_dict()
    result = get_job_results(job)
    collect_identities(job, result)
