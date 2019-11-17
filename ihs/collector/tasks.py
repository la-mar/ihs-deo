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
    ProducingEntityList,
    Collector,
)
from collector.identity_list import IdentityList
from config import get_active_config, project, IdentityTemplates, ExportDataTypes
import metrics

logger = logging.getLogger(__name__)

conf = get_active_config()
endpoints = Endpoint.load_from_config(conf)


def run_endpoint_task(
    endpoint_name: str, task_name: str
) -> Generator[ExportJob, None, None]:
    """ Unpack an tasks options and submit a job for each option set """
    endpoint = endpoints[endpoint_name]
    requestor = ExportBuilder(conf.API_BASE_URL, endpoint)
    task = endpoint.tasks[task_name]
    for opts in task.options:
        ep = ExportParameter(**opts)
        yield requestor.submit(
            ep,
            metadata={
                "endpoint": endpoint_name,
                "task": task_name,
                "url": conf.API_BASE_URL,
                **opts,
            },
        )


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
            data = WellboreTransformer.extract_from_well_set(document)
        elif job.data_type == ExportDataTypes.PRODUCTION.value:
            data = ProductionTransformer.extract_from_production_set(document)
        collector.save(data)


def collect_identities(job: ExportJob, data: bytes) -> IdentityList:
    interface = None
    if job.data_type == ExportDataTypes.WELL.value:
        interface = WellList(job.name, job.criteria.get("hole_direction"))
        interface.ids = data
    elif job.data_type == ExportDataTypes.PRODUCTION.value:
        interface = ProducingEntityList(job.name, job.criteria.get("hole_direction"))
        interface.ids = data

    return interface


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

    from ihs import create_app

    logging.basicConfig(level=20)
    app = create_app()
    app.app_context().push()

    endpoint_name = "well_master_horizontal"
    task_name = "sync"
    results = [x for x in run_endpoint_task(endpoint_name, task_name) if x is not None]
    job = results[0]
    [collect(r) for r in results]
    # [r.to_dict().get("name") for r in results]

    endpoint_name = "wells"
    task_name = "driftwood"
    results = [x for x in run_endpoint_task(endpoint_name, task_name) if x is not None]
    [collect(r) for r in results]
