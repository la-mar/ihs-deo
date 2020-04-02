from __future__ import annotations

import logging
from typing import Dict, Generator, Union, List
from datetime import date, timedelta, datetime

import metrics
from api.models import *  # noqa
from api.models import ChangeDeleteLog
from collector import ExportJob  # noqa
from collector import (
    Collector,
    Endpoint,
    ExportBuilder,
    ExportParameter,
    ExportRetriever,
    ProductionList,
    ProductionTransformer,
    WellboreTransformer,
    WellList,
    XMLParser,
    CDExporter,
)
from collector.identity_list import IdentityList
from config import ExportDataTypes, IdentityTemplates, get_active_config
from ihs import create_app

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
                **opts,  # duplicate job options here to they travel with the job
                # throughout its lifecycle
            },
        )
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
    data = retr.get(auto_delete=True)
    return data


def collect_data(job: ExportJob, xml: bytes):
    if xml:
        parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
        document = parser.parse(xml)
        model = endpoints[job.endpoint].model
        collector = Collector(model)
        if job.data_type == ExportDataTypes.WELL.value:
            data = WellboreTransformer.extract_from_collection(document, model=model)
        elif job.data_type == ExportDataTypes.PRODUCTION.value:
            data = ProductionTransformer.extract_from_collection(document, model=model)
        collector.save(data, replace=True)


def collect_identities(job: ExportJob, data: bytes) -> IdentityList:
    interface = None
    if job.data_type == ExportDataTypes.WELL.value:
        interface = WellList(job.name, job.criteria.get("hole_direction"))
        interface.ids = data
    elif job.data_type == ExportDataTypes.PRODUCTION.value:
        interface = ProductionList(job.name, job.criteria.get("hole_direction"))
        interface.ids = data

    return interface


# def delete_job(job: ExportJob) -> bool:
#     endpoint = endpoints[job.endpoint]
#     requestor = ExportBuilder(endpoint)
#     result = False
#     if requestor.job_exists(job):
#         result = requestor.delete_job(job)
#     return result


def purge_remote_exports() -> bool:
    eb = ExportBuilder(None)
    eb.delete_all_jobs()
    return True


def calc_remote_export_capacity(njobs: int = None) -> Dict[str, Union[float, int]]:
    """Calculate the amount of storage space currently consumed by job exports on IHS' servers.

    Returns:
        dict -- {
                 capacity_used: space used in KB,
                 njobs: number of existing completed jobs
    """
    mean_doc_size_bytes = (
        40000 * conf.TASK_BATCH_SIZE
    )  # average single entity document size
    inflation_pct = 0.1  # over estimate the used capacity by this percentage
    doc_size_bytes = mean_doc_size_bytes + (inflation_pct * mean_doc_size_bytes)
    remote_capacity_bytes = 1000000000  # 1 GB
    if not njobs:
        eb = ExportBuilder(None)
        njobs = len(eb.list_completed_jobs())
    return {
        "remote.capacity.used": njobs * doc_size_bytes,
        "remote.capacity.available": remote_capacity_bytes - (njobs * doc_size_bytes),
        "remote.capacity.total": remote_capacity_bytes,
        "remote.jobs": njobs,
    }


def download_changes_and_deletes() -> int:
    max_date = ChangeDeleteLog.max_date()
    max_sequence = ChangeDeleteLog.max_sequence() or 0

    today = datetime.now()

    if max_date:
        last_date = max_date - timedelta(days=1)
    else:
        last_date = date.today() - timedelta(days=30)

    cde = CDExporter(from_date=last_date, to_date=today)

    results = cde.get_all()
    logger.info(f"Downloaded {len(results)} changes and deletes")

    records: List[Dict] = []
    for r in results:
        new = {}
        for k, v in r.items():
            if v is not None:
                if "uwi" in k:
                    v = str(v)

                if k == "reasoncode":
                    k = "reason_code"
                elif k == "activecode":
                    k = "active_code"
                elif k == "referenceuwi":
                    k = "reference_uwi"
                elif k == "newuwi":
                    k = "new_uwi"

                new[k] = v

        if new.get("sequence", 0) > max_sequence:
            new["processed"] = False

            records.append(new)

    logger.info(
        f"Found {len(records)} changes and deletes (filtered {len(results) - len(records)})"
    )
    collector = Collector(ChangeDeleteLog)
    return collector.save(records)


# def process_changes_and_deletes():
#     # reason_action_map = {
#     #     "no_action": [0, 6],
#     #     "update_to_new_uwi": [1, 5, 7, 8, 9],
#     #     "update_to_ref_uwi": [2],
#     #     "delete": [3, 4],
#     # }
#     reason_action_map = {
#         0: "no_action",
#         1: "update_to_new_uwi",
#         2: "update_to_ref_uwi",
#         3: "delete",
#         4: "delete",
#         5: "update_to_new_uwi",
#         6: "no_action",
#         7: "update_to_new_uwi",
#         8: "update_to_new_uwi",
#         9: "update_to_new_uwi",
#     }

#     objs = ChangeDeleteLog.objects(processed=False)

#     obj = objs[len(objs) - 80]
#     obj._data
#     #! unfinished

#     # for obj in objs:
#     #     if obj.processed is False:
#     #         action = reason_action_map[obj.reason_code]

#     #         if action == "delete":
#     #             document = WellHorizontal.objects(api14=obj.uwi).first()
#     #             document = WellVertical.objects(api14=obj.uwi).first()


if __name__ == "__main__":

    from time import sleep

    logging.basicConfig(level=10)
    app = create_app()
    app.app_context().push()

    endpoint_name = "well_horizontal"
    task_name = "endpoint_check"
    endpoint = endpoints[endpoint_name]
    task = endpoint.tasks[task_name]
    configs = []
    for opts in task.options:
        job_config = dict(
            job_options=opts,
            metadata={
                "endpoint": endpoint_name,
                "task": task_name,
                "url": conf.API_BASE_URL,
                "hole_direction": opts.get("criteria", {}).get("hole_direction"),
                **opts,  # duplicate job options here to they travel with the job
                # throughout its lifecycle
            },
        )
        configs.append(job_config)

    job_options, metadata = configs[0].values()
    ep = ExportParameter(**job_options)
    print(ep.params["Query"])
    requestor = ExportBuilder(endpoint)

    job = submit_job(job_options=job_options, metadata=metadata)
    job
    sleep(3)

    xml = get_job_results(job)
    parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
    document = parser.parse(xml)
    model = endpoint.model
    data = WellboreTransformer.extract_from_collection(document, model=model)
    len(data)
    [x["api14"] for x in data]
    collector = Collector(model)
    collector.save(data, replace=True)
