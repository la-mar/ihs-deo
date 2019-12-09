from __future__ import annotations
from typing import Union, Generator, Dict
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
from collector import Endpoint, Collector
from config import get_active_config, IdentityTemplates, ExportDataTypes
import metrics

logger = logging.getLogger(__name__)

conf = get_active_config()
endpoints = Endpoint.load_from_config(conf)


def run_endpoint_task(
    endpoint_name: str, task_name: str
) -> Generator[dict, None, None]:
    """ Unpack task options and assemble metadata for job configuration """
    endpoint = endpoints[endpoint_name]
    task = endpoint.tasks[task_name]
    metrics.post(
        "task.execution", 1, tags={"endpoint": endpoint_name, "task": task_name}
    )
    for opts in task.options:
        job_config = dict(
            job_options=opts,
            metadata={
                "endpoint": endpoint_name,
                "task": task_name,
                "url": conf.API_BASE_URL,
                "hole_direction": opts.get("criteria", {}).get("hole_direction"),
                **opts,  # duplicate job options here to they travel with the job throughout its lifecycle
            },
        )
        metrics.post("task.job.created", 1, tags=job_config.get("metadata"))
        yield job_config


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


def purge_remote_exports() -> bool:
    eb = ExportBuilder(None)
    eb.delete_all_jobs()
    return True


def calc_remote_export_capacity() -> Dict[str, Union[float, int]]:
    """Calculate the amount of storage space currently consumed by job exports on IHS' servers.

    Returns:
        dict -- {
                 capacity_used: space used in KB,
                 njobs: number of existing completed jobs
    """
    mean_doc_size_bytes = 90000
    inflation_pct = 0.25
    doc_size_bytes = mean_doc_size_bytes + (0.25 * mean_doc_size_bytes)
    remote_capacity_bytes = 1000000000  # 1 GB
    eb = ExportBuilder(None)
    njobs = len(eb.list_completed_jobs())
    return {
        "remote.capacity.used": njobs * doc_size_bytes,
        "remote.capacity.available": remote_capacity_bytes - (njobs * doc_size_bytes),
        "remote.capacity.total": remote_capacity_bytes,
        "remote.jobs": njobs,
    }


if __name__ == "__main__":
    # pylint: disable-all

    from ihs import create_app

    logging.basicConfig(level=10)
    app = create_app()
    app.app_context().push()

    # x = list(run_endpoint_task(endpoint_name, task_name))[0]

    endpoint_name = "production_horizontal"
    task_name = "driftwood"
    results = [x for x in run_endpoint_task(endpoint_name, task_name) if x is not None]
    opts = results[0]
    opts.get("job_options")
    job = submit_job(**opts)
    job.to_dict()
    result = get_job_results(job)
    collect_data(job, result)

    endpoint_name = "well_horizontal"
    task_name = "sequoia"
    results = [x for x in run_endpoint_task(endpoint_name, task_name) if x is not None]
    opts = results[0]
    opts.get("job_options")
    job = submit_job(**opts)
    job.to_dict()
    result = get_job_results(job)
    collect_data(job, result)

    endpoint_name = "production_master_horizontal"
    task_name = "sync"
    results = [x for x in run_endpoint_task(endpoint_name, task_name) if x is not None]
    opts = results[0]
    opts.get("job_options")
    job = submit_job(**opts)
    job.to_dict()
    result = get_job_results(job)
    collect_identities(job, result)

    endpoint_name = "well_master_horizontal"
    task_name = "sync"
    results = [x for x in run_endpoint_task(endpoint_name, task_name) if x is not None]

    opts = results[5]  # tx-bailey
    job = submit_job(**opts)
    if job:
        get_job_results(job)

    endpoint_name = "production_master_vertical"
    task_name = "sync"
    results = [x for x in run_endpoint_task(endpoint_name, task_name) if x is not None]
    opts = results[0]
    # opts.get("job_options")
    job = submit_job(**opts)
    job.to_dict()
    result = get_job_results(job)
    collect_identities(job, result)
