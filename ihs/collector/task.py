from __future__ import annotations

import logging
from pydoc import locate
from typing import Dict, List, Union, Optional, Any
from datetime import datetime, timedelta
import pytz

from celery.schedules import crontab
import util
from celery.utils.time import humanize_seconds

from api.models import *  # noqa
from api.models import (
    Model,
    County,
    WellMasterHorizontal,
    WellMasterVertical,
    ProductionMasterHorizontal,
    ProductionMasterVertical,
)

from config import get_active_config, IdentityTemplates

conf = get_active_config()

logger = logging.getLogger(__name__)


class OptionMatrix:
    batch_size: int = conf.TASK_BATCH_SIZE

    def __init__(
        self,
        target_model: str,
        task_name: str,
        matrix: dict = None,
        data_type: str = None,
        template: str = None,
        criteria: Dict = None,
        force: bool = False,
        **kwargs,
    ):
        self.target_model: str = target_model
        self.target_model_name: str = self.target_model.split(".")[-1]
        self.task_name: str = task_name
        self.data_type = data_type
        self.template = template
        self.criteria = criteria or {}
        # self.hole_direction = self.criteria.get("hole_direction")
        self.matrix: Dict = {k: v for k, v in (matrix or {}).items()}
        self.kwargs: Dict = kwargs
        self.using: Optional[str] = self.matrix.pop("using", None)
        self.label: str = self.matrix.pop("label", "values")
        self.use_next_county: bool = self.matrix.pop("next_county", None)
        self.batch_size: int = self.matrix.pop("batch_size", 10) or self.batch_size
        self.source_name: Optional[str] = None
        self.force = force

    def __repr__(self):
        return str(self.to_list())

    def __iter__(self):
        for d in self.to_list():
            yield d

    def make_option_set_name(self, name: str = None) -> str:
        if self.is_identity_export and name is not None:
            return name
        else:
            source_name = self.source_name or "yaml"
            target_model_name = self.target_model_name or ""
            name = name or ""
            return f"{source_name} -> {target_model_name} ({name})"

    def generate(self) -> List[Dict]:
        """ Generate the option matrix from the instance's parameters """

    @property
    def is_identity_export(self) -> bool:
        return IdentityTemplates.has_member(self.template)

    def _cross_apply(self) -> List[Dict]:
        # if self.matrix.get("values"):
        #     pass
        if self.is_identity_export:
            if not self.matrix:
                self.matrix = self._matrix_for_identity_export()
        elif self.using:
            self.matrix = self._matrix_from_model()
        elif self.use_next_county:
            self.matrix = self._matrix_from_county()
        else:
            logger.debug(f"({self.target_model_name}) No matrix to generate")

        optset = []
        if len(self.matrix):
            for key, value in self.matrix.items():
                v = {
                    # "name": key,
                    "name": self.make_option_set_name(key),
                    "source_name": self.source_name,
                    "target_model": self.target_model_name,
                    "data_type": self.data_type,
                    "template": self.template,
                    "criteria": self.criteria,
                    **self.kwargs,
                }

                if isinstance(value, dict):
                    v.update(**value)
                else:
                    v[key] = value
                optset.append(v)
        else:
            optset = [
                {
                    "name": self.make_option_set_name(self.task_name),
                    "source_name": self.source_name,
                    "target_model": self.target_model_name,
                    "data_type": self.data_type,
                    "template": self.template,
                    "criteria": self.criteria,
                    **self.kwargs,
                }
            ]

        return optset

    def to_list(self) -> List[Dict]:
        return self._cross_apply()

    def _matrix_for_identity_export(self) -> Dict[str, Dict]:
        logger.debug(f"({self.target_model_name}) Generating Identity Matrix")
        source_model = County
        source_model_name = County.__name__
        criteria: Dict[str, Dict] = {}
        utcnow = pytz.utc.localize(datetime.utcnow())

        if not self.is_identity_export:
            raise ValueError(
                f"({self.target_model_name}) Cant generate identity matrix for non-identity export tasks"  # noqa
            )

        if self.target_model_name == "WellMasterHorizontal":
            attr = "well_h_ids_last_run"
        elif self.target_model_name == "WellMasterVertical":
            attr = "well_v_ids_last_run"
        elif self.target_model_name == "ProductionMasterHorizontal":
            attr = "prod_h_ids_last_run"
        elif self.target_model_name == "ProductionMasterVertical":
            attr = "prod_v_ids_last_run"
        else:
            raise ValueError(
                f"Unable to determine target model from {self.target_model_name}"
            )

        self.source_name = source_model.__name__
        county_obj, attr, last_run, is_ready, cooldown = County.next_available(attr)

        if is_ready:
            if county_obj:
                criteria[county_obj.name] = {
                    "state_code": county_obj.state_code,
                    "county_code": county_obj.county_code,
                }

                county_obj[attr] = utcnow
                county_obj.save()
                logger.warning(
                    f"({source_model_name}) updated {county_obj.name}.{attr}: {last_run} -> {utcnow}"
                )
        else:
            next_run_in_seconds = (
                (last_run + timedelta(hours=cooldown)) - utcnow
            ).total_seconds()
            logger.warning(
                f"({self.target_model_name}) skipping {county_obj.name}: next available for run in {humanize_seconds(next_run_in_seconds)}"  # noqa
            )

        # bypass _to_batches and return criteria dict directly so it is expanded into
        # the job's options and subsequently passed to the query formatter as template variables
        return criteria

    def _matrix_from_model(self) -> Dict[str, Dict]:
        """ Generate a matrix using the values from model column referenced in the
            task's options.
        """
        logger.debug(f"({self.target_model_name}) Generating Matrix from Model")

        ids: List[str] = []

        if self.using:
            model_name, field_name = self.using.rsplit(".", maxsplit=1)
            model = self.locate_model(model_name)
            self.source_name = model_name

            for document in model.objects():
                ids = ids + document[field_name]

        return self._to_batches(values=ids)

    def _matrix_from_county(self) -> Dict[str, Dict]:
        logger.debug(f"({self.target_model_name}) Generating Matrix from County")

        county_obj = None
        ids = []
        utcnow = pytz.utc.localize(datetime.utcnow())

        if self.target_model_name == "WellHorizontal":
            attr = "well_h_last_run"
            model = WellMasterHorizontal
        elif self.target_model_name == "WellVertical":
            attr = "well_v_last_run"
            model = WellMasterVertical
        elif self.target_model_name == "ProductionHorizontal":
            attr = "prod_h_last_run"
            model = ProductionMasterHorizontal
        elif self.target_model_name == "ProductionVertical":
            attr = "prod_v_last_run"
            model = ProductionMasterVertical

        county_obj, attr, last_run, is_ready, cooldown = County.next_available(attr)
        self.source_name = county_obj.name

        if is_ready or self.force:
            model_obj = model.objects(name=county_obj.name).first()
            if model_obj:
                ids = model_obj.ids

                county_obj[attr] = utcnow
                county_obj.save()
                logger.warning(
                    f"({county_obj.name}) updated {county_obj.name}.{attr}: {last_run} -> {utcnow}"
                )
        else:
            next_run_in_seconds = (
                (last_run + timedelta(hours=cooldown)) - utcnow
            ).total_seconds()
            logger.warning(
                f"({self.target_model_name}) Skipping {self.source_name} next available for run in {humanize_seconds(next_run_in_seconds)}"  # noqa
            )  # noqa

        return self._to_batches(values=ids)

    def _to_batches(self, values: List[Any], batch_size: int = None) -> Dict[str, Dict]:
        """ Chunk a list of values into smaller batches """

        batch_size = batch_size or self.batch_size

        matrix = {}
        for idx, chunk in enumerate(util.chunks(values, batch_size)):
            chunk_count = len(chunk)
            subset_name = (
                f"{self.label}[{chunk_count * idx}:{chunk_count * (idx+1)}]"  # noqa
            )
            matrix[subset_name] = {self.label: chunk}

        if len(values):
            logger.warning(
                f"({self.target_model_name}) Compressed {len(values)} ids into {len(matrix)} option sets from {self.source_name}"  # noqa
            )

        return matrix

    def locate_model(self, model_name: str) -> Model:  # type: ignore
        model: Model = None  # type: ignore
        try:
            # try to import dotted model name. ex: api.models.MyModel
            model = locate(model_name)
        except ModuleNotFoundError:
            try:
                # try to import model from global namespace
                model = globals()[model_name]
            except ModuleNotFoundError:
                raise ModuleNotFoundError(
                    f"No module named '{model_name}' found in project or global namespace"
                )
        except Exception as e:
            raise Exception(f"({self.target_model_name}) Unable to locate model -- {e}")

        return model


class Task:
    """ A yaml defined task object to be passed to Celery """

    def __init__(
        self,
        model_name: str,
        task_name: str,
        cron: dict = None,
        seconds: int = None,
        options: dict = None,
        enabled: bool = True,
        endpoint_name: str = None,
        **kwargs,
    ):
        self.model_name = model_name
        self.task_name = task_name
        self.endpoint_name = endpoint_name
        self.cron = self.parse_cron(cron or {})
        self.seconds = seconds
        self.options = OptionMatrix(
            target_model=model_name, task_name=task_name, **(options or {})
        )
        self.enabled = enabled

        if not any([self.cron, self.seconds]):
            raise ValueError("Either seconds or cron must be specified")

    def __repr__(self):
        status = "***DISABLED***" if not self.enabled else ""
        s = self.schedule
        sch = (
            f"{s._orig_minute} {s._orig_hour} {s._orig_day_of_week} {s._orig_day_of_month} {s._orig_month_of_year}"  # noqa
            if self.seconds is None
            else f"({self.schedule} seconds)"
        )
        return f"{status} {self.qualified_name} {sch}"

    @property
    def qualified_name(self):
        return f"{self.endpoint_name or self.model_name}.{self.task_name}"

    @property
    def schedule(self) -> Union[crontab, int]:
        """ The scheduling expression to be used for task creation.
         Prefers seconds over cron expressions. """
        return self.seconds or self.cron

    @staticmethod
    def parse_cron(cron: dict):
        """ Return a crontab object if the passed dict has any non-null values """
        notnull = {k: v for k, v in cron.items() if v is not None}
        if len(notnull) > 0:
            return crontab(**notnull)
        else:
            return None

    @property
    def configs(self) -> List[Dict]:
        """ Generate a list of discrete export configurations """
        configs = []
        for opts in self.options:
            job_config = dict(
                job_options=opts,
                metadata={
                    "endpoint": self.endpoint_name,
                    "task": self.task_name,
                    "url": conf.API_BASE_URL,
                    "hole_direction": opts.get("criteria", {}).get("hole_direction"),
                    "data_type": opts.get("data_type"),
                    "target_model": opts.get("target_model"),
                    "source_name": opts.get("source_name"),
                    "name": opts.get("name"),
                },
            )
            configs.append(job_config)
        return configs


if __name__ == "__main__":
    logger.setLevel(10)

    from config import get_active_config
    from attrdict import AttrDict
    from ihs.config import get_active_config
    from collector import Endpoint
    from ihs import create_app, db
    from collector.xml_query import XMLQuery

    conf = get_active_config()
    app = create_app()
    app.app_context().push()

    conf = get_active_config()
    # endpoints = Endpoint.from_yaml("tests/data/collector.yaml")
    endpoints = Endpoint.from_yaml("config/collector.yaml")
    # task = endpoints["well_horizontal"].tasks["endpoint_check"]
    task = endpoints["well_horizontal"].tasks["endpoint_check"]

    task = Task(
        model_name="api.models.WellHorizontal",
        task_name="sync",
        endpoint_name="well_horizontal",
        cron={"minute": 0, "hour": 12},
        options={
            "matrix": {
                "check": {
                    "values": ["42461409160000", "42383406370000", "42461412100000"]
                }
            },
            "data_type": "Well",
            "template": "EnerdeqML Well",
            "criteria": {"hole_direction": "H"},
        },
    )

    from api.models import County

    matrix = (
        County.as_df()
        .reset_index()
        .loc[:, ["name", "county_code", "state_code"]]
        .to_dict(orient="records")
    )

    # County.as_df().reset_index().loc[:, ["name", "county_code", "state_code"]].values

    tasks: List[Task] = []
    for county_params in matrix:
        task = Task(
            model_name="api.models.WellMasterHorizontal",
            task_name="sync",
            endpoint_name="well_master_horizontal",
            cron={"minute": 0, "hour": 12},
            options={
                "matrix": county_params,  # {"values": matrix},
                "data_type": "Well",
                "template": "Well ID List",
                "query_path": "well_by_county.xml",
                "criteria": {"hole_direction": "H"},
                "hole_direction": "H",
                **county_params,
            },
        )
        # tasks.append(task)

        job_options, metadata = task.configs[0].values()
        ep = ExportParameter(**job_options)

        print(ep.params["Query"])
        endpoint = endpoints["well_master_horizontal"]
        task = endpoint.tasks["sync"]
        requestor = ExportBuilder(endpoint)

        job = submit_job(job_options=job_options, metadata=metadata)
        # job.to_dict()

        sleep(5)

        if job:
            collect(job)
    # task = Task(
    #     model_name="api.models.WellMasterHorizontal",
    #     task_name="sync",
    #     endpoint_name="well_master_horizontal",
    #     cron={"minute": 0, "hour": 12},
    #     options={
    #         "data_type": "Well",
    #         "template": "Well ID List",
    #         "criteria": {"hole_direction": "H"},
    #     },
    # )

    # list(task.options)[0]
    c = list(task.configs)[0]
    c

    api14s = [
        "42461409160000",
        "42383406370000",
        "42461412100000",
        "42461412090000",
        "42461411750000",
        "42461411740000",
        "42461411730000",
        "42461411720000",
        "42461411600000",
        "42461411280000",
        "42461411270000",
        "42461411260000",
        "42383406650000",
        "42383406640000",
        "42383406400000",
        "42383406390000",
        "42383406380000",
        "42461412110000",
        "42383402790000",
        "42461397940000",
    ]

    from api.models import County, WellMasterHorizontal

    county = County.objects(name="tx-upton").get()
    county.well_h_last_run = None
    county.save()

    id_master = WellMasterHorizontal.objects(name="tx-upton").get()
    id_master.ids = api14s
    id_master.count = len(api14s)
    id_master.save()
    id_master._data
