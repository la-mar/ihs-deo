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
from exc import CollectorError
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
    for config in task.configs:
        yield config


def submit_job(job_options: dict, metadata: dict) -> ExportJob:
    endpoint_name = metadata.get("endpoint")
    endpoint = endpoints[endpoint_name]
    ep = ExportParameter(**job_options)
    requestor = ExportBuilder(endpoint)
    return requestor.submit(ep, metadata=metadata or {})


def collect(job: Union[dict, ExportJob]):
    if isinstance(job, dict):
        job = ExportJob(**job)

    is_identity_export = IdentityTemplates.has_member(job.template)
    data = get_job_results(job)

    if is_identity_export:
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
        data: List[Dict] = []
        if job.data_type == ExportDataTypes.WELL.value:
            data = WellboreTransformer.extract_from_collection(document, model=model)
        elif job.data_type == ExportDataTypes.PRODUCTION.value:
            data = ProductionTransformer.extract_from_collection(document, model=model)

        metrics.post("job.collection.success", len(data), tags=job.limited_dict())
        collector.save(data, replace=True)


def collect_identities(job: ExportJob, data: bytes) -> IdentityList:
    interface = None
    if job.data_type == ExportDataTypes.WELL.value:
        interface = WellList(job.name, job.hole_direction)
        interface.ids = data
    elif job.data_type == ExportDataTypes.PRODUCTION.value:
        interface = ProductionList(job.name, job.hole_direction)
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


# def calc_remote_export_capacity(njobs: int = None) -> Dict[str, Union[float, int]]:
#     """Calculate the amount of storage space currently consumed by job exports on IHS' servers.

#     Returns:
#         dict -- {
#                  capacity_used: space used in KB,
#                  njobs: number of existing completed jobs
#     """
#     mean_doc_size_bytes = 18000 * conf.TASK_BATCH_SIZE
#     inflation_pct = 0.1
#     doc_size_bytes = mean_doc_size_bytes + (inflation_pct * mean_doc_size_bytes)
#     remote_capacity_bytes = 1000000000  # 1 GB
#     if not njobs:
#         eb = ExportBuilder(None)
#         njobs = len(eb.list_completed_jobs())

#     return {
#         "remote.capacity.used": njobs * doc_size_bytes,
#         "remote.capacity.available": remote_capacity_bytes - (njobs * doc_size_bytes),
#         "remote.capacity.total": remote_capacity_bytes,
#         "remote.jobs": njobs,
#     }


def calc_remote_export_capacity() -> Dict[str, Union[float, int]]:
    """Calculate the amount of storage space currently consumed by job exports on IHS' servers.

    Returns:
        dict -- {
                 capacity_used: space used in KB,
                 njobs: number of existing completed jobs
    """
    mean_doc_size_bytes = (
        18000 * conf.TASK_BATCH_SIZE
    )  # average single entity document size
    inflation_pct: float = 0.25  # over estimate the used capacity by this percentage
    doc_size_bytes = mean_doc_size_bytes + (inflation_pct * mean_doc_size_bytes)
    remote_capacity_bytes: int = 1000000000  # 1 GB
    eb = ExportBuilder(None)
    try:
        njobs = len(eb.list_completed_jobs())
    except CollectorError as e:
        logger.exception(f"Unable to calculate export capacity -- {e}", stack_info=True)
        return {}

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


# if __name__ == "__main__":

#     from time import sleep
#     from uuid import UUID

#     logging.basicConfig(level=10)
#     app = create_app()
#     app.app_context().push()

#     # endpoint_name = "well_master_vertical"
#     endpoint_name = "production_master_vertical"
#     task_name = "sync"
#     endpoint = endpoints[endpoint_name]
#     task = endpoint.tasks[task_name]
#     configs = task.configs
#     job_options, metadata = configs[0].values()
#     ep = ExportParameter(**job_options)
#     print(ep.params["Query"])
#     requestor = ExportBuilder(endpoint)

#     job = submit_job(job_options=job_options, metadata=metadata)
#     job.to_dict()
#     {
#         "job_id": "exports/8e89d1bc-e83f-43d9-a91d-cc60a69bf2b2.txt",
#         "endpoint": "production_master_vertical",
#         "task": "sync",
#         "url": "http://www.ihsenergy.com",
#         "hole_direction": "V",
#         "data_type": "Production Allocated",
#         "target_model": "ProductionMasterVertical",
#         "source_name": "County",
#         "name": "tx-midland",
#         "domain": "US",
#         "template": "Production ID List",
#         "query": "<criterias>...</criterias>",
#         "overwrite": True,
#         "export_filename": UUID("8e89d1bc-e83f-43d9-a91d-cc60a69bf2b2"),
#     }

#     sleep(3)

#     collect(job)

# xml = get_job_results(job)
# parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
# document = parser.parse(xml)
# model = endpoint.model
# data = WellboreTransformer.extract_from_collection(document, model=model)
# len(data)
# [x["api14"] for x in data]
# collector = Collector(model)
# collector.save(data, replace=True)

# calc_remote_export_capacity()["remote.capacity.used"] * 1e-6
