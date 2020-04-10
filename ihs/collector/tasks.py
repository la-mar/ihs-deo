from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Dict, Generator, List, Optional, Union, Tuple

import pandas as pd

import metrics
from api.models import (  # noqa
    ChangeDeleteLog,
    County,
    ProductionHorizontal,
    ProductionMasterHorizontal,
    ProductionMasterVertical,
    ProductionVertical,
    WellHorizontal,
    WellMasterHorizontal,
    WellMasterVertical,
    WellVertical,
)
from collector import ExportJob  # noqa
from collector import (
    CDExporter,
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
)
from collector.identity_list import IdentityList
from collector.task import Task
from config import ExportDataTypes, IdentityTemplates, get_active_config
from exc import CollectorError, NoIdsError
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


def submit_job(job_options: dict, metadata: dict) -> Optional[ExportJob]:
    endpoint_name = metadata.get("endpoint")
    endpoint = endpoints[endpoint_name]
    # name = metadata.get("name", None)
    target_model = metadata.get("target_model", None)
    task_name = metadata.get("task", None)
    source_name = metadata.get("source_name", None)

    try:
        ep = ExportParameter(**job_options)
        requestor = ExportBuilder(endpoint)
        job = requestor.submit(ep, metadata=metadata or {})
        return job
    except CollectorError as e:
        logger.warning(
            f"({target_model}) Skipping job {task_name} -> {source_name}: {e}"
        )
        return None


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
    inflation_pct: float = 0.1  # over estimate the used capacity by this percentage
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


def synchronize_master_lists():
    county_model_name = County.__name__.split(".")[-1]
    master_counties = County.as_df().index.tolist()

    for model in [
        WellMasterHorizontal,
        WellMasterVertical,
        ProductionMasterHorizontal,
        ProductionMasterVertical,
    ]:
        target_model_name = model.__name__.split(".")[-1]
        model_counties = model.as_df().index.tolist()
        missing_from_model = [x for x in master_counties if x not in model_counties]

        # add missing counties to model
        added = []
        for county in missing_from_model:
            i = model(name=county)
            i.save()
            added.append(county)

        if added:
            logger.info(
                f"({target_model_name}) Added {len(added)} entries from {county_model_name} master: {added}"  # noqa
            )
        missing_from_master = [x for x in model_counties if x not in master_counties]
        if missing_from_master:
            logger.info(
                f"({target_model_name}) has {len(missing_from_master)} entries missing from {county_model_name} master"  # noqa
            )

        logger.info(f"({target_model_name}) synchronized to {county_model_name} master")


def refresh_master_lists() -> List[Tuple[List[Dict], str, str]]:
    endpoints = Endpoint.from_yaml(conf.COLLECTOR_CONFIG_PATH)
    endpoints = {
        k: v for k, v in endpoints.items() if "master" in v.model.__name__.lower()
    }

    all_endpoint_configs: List[Tuple[List[Dict], str, str]] = []
    for endpoint_name, endpoint in endpoints.items():
        # endpoint_name, endpoint = list(endpoints.items())[0]
        target_model_name = endpoint.model.__name__.split(".")[-1]

        county_record_dict = (
            County.as_df().loc[:, ["county_code", "state_code"]].to_dict(orient="index")
        )

        task = endpoint.tasks["sync"]
        task.options.matrix = county_record_dict  # override the yaml defined matrix
        configs = task.configs
        logger.warning(f"({target_model_name}) refreshing {len(configs)} counties")
        all_endpoint_configs.append((configs, endpoint_name, task.task_name))

    return all_endpoint_configs
    # job_options, metadata = task.configs[0].values()
    # ep = ExportParameter(**job_options)
    # print(ep.params["Query"])


if __name__ == "__main__":

    import loggers

    loggers.config(10)
    logging.getLogger("collector.parser").setLevel(30)
    logging.getLogger("zeep").setLevel(30)
    from time import sleep

    # from uuid import UUID
    from ihs import create_app

    logging.basicConfig(level=10)
    app = create_app()
    app.app_context().push()

    # endpoint_name = "well_master_vertical"
    # endpoint_name = "well_master_vertical"
    # task_name = "sync"
    # endpoint = endpoints[endpoint_name]
    # task = endpoint.tasks[task_name]
    # # configs =
    # job_options, metadata = task.configs[0].values()

    # for configs, endpoint_name, task_name in refresh_master_lists():
    #     for job
    #     ep = ExportParameter(**job_options)
    #     print(ep.params["Query"])
    #     requestor = ExportBuilder(endpoint)

    #     job = submit_job(job_options=job_options, metadata=metadata)
    #     # job.to_dict()

    #     sleep(5)

    #     if job:
    #         collect(job)

# xml = get_job_results(job)
# parser = XMLParser.load_from_config(conf.PARSER_CONFIG)
# document = parser.parse(xml)
# model = endpoint.model
# data = WellboreTransformer.extract_from_collection(document, model=model)
# len(data)
# [x["api14"] for x in data]
# collector = Collector(model)
# collector.save(data, replace=True)
# from api.models import County, WellMasterHorizontal
# import pandas as pd

# df = pd.DataFrame([x._data for x in County.objects.all()]).set_index("name")
# df.columns
# df = df.drop(columns=["state_code", "county_code"]).sort_values("well_h_last_run")
# df.shape

# hz_ids = (
#     pd.DataFrame([x._data for x in WellMasterHorizontal.objects.all()])
#     .set_index("name")
#     .sort_index()
# )
# hz_ids.loc[~hz_ids.index.str.contains("County")].shape

# joined = df.join(hz_ids.ids)
# joined[joined.ids.isna()]


# # data[7]
# self = task.options
