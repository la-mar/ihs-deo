from __future__ import annotations

from pydoc import locate
from typing import Dict, List, Union

from celery.schedules import crontab
import util

from api.models import *  # noqa
from api.models import Model

from config import get_active_config

conf = get_active_config()


class OptionMatrix:
    batch_size: int = conf.TASK_BATCH_SIZE

    def __init__(self, matrix: dict = None, **kwargs):
        self.matrix = {k: v for k, v in (matrix or {}).items()}
        self.kwargs = kwargs
        self.using = self.matrix.pop("using", None)
        self.label = self.matrix.pop("label", "values")
        self.batch_size = self.matrix.pop("batch_size", 10) or self.batch_size

    def __repr__(self):
        return str(self.to_list())

    def __iter__(self):
        for d in self._cross_apply():
            yield d

    def generate(self) -> List[Dict]:
        """ Generate the option matrix from the instance's parameters """

    def _cross_apply(self) -> List[Dict]:
        if self.using:
            self.matrix = self._matrix_from_model()

        optset = []
        if len(self.matrix):
            for key, value in self.matrix.items():
                v = {"name": key, **self.kwargs}
                if isinstance(value, dict):
                    v.update(**value)
                else:
                    v[key] = value
                optset.append(v)
        else:
            optset = [self.kwargs or {}]

        return optset

    def to_list(self) -> List[Dict]:
        return self._cross_apply()

    def _matrix_from_model(self) -> Dict[str, Dict]:
        """Generate a matrix using the values in a referenced model field.

        Arguments:
            model_ref {str} -- Model reference string of the form module.models.model.field.
                               Ex: api.models.WellMasterHorizontal.ids
        """

        model_name, field_name = self.using.rsplit(".", maxsplit=1)
        model = self.locate_model(model_name)

        values: List[str] = []
        for document in model.objects():
            values = values + document[field_name]

        matrix = {}
        # total_count = len(values)
        for idx, chunk in enumerate(util.chunks(values, self.batch_size)):
            chunk_count = len(chunk)
            subset_name = (
                f"{self.label}[{chunk_count * idx}:{chunk_count * (idx+1)}]"  # noqa
            )
            matrix[subset_name] = {self.label: chunk}

        return matrix

    def _matrix_from_ids(self) -> List[Dict]:
        """ Generate a matrix from a delimited string or list of identifiers """

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
            raise Exception(f"Unable to locate module {model_name} -- {e}")

        return model


class Task:
    """ A yaml defined task object to be passed to Celery """

    def __init__(
        self,
        model_name: str,
        task_name: str,
        cron: dict = None,
        seconds: int = None,
        mode: str = None,
        options: dict = None,
        enabled: bool = True,
        **kwargs,
    ):
        self.model_name = model_name
        self.task_name = task_name
        self.cron = self.parse_cron(cron or {})
        self.seconds = seconds
        self.mode = mode
        self.options = OptionMatrix(**(options or {}))
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
        return f"{self.model_name}.{self.task_name}"

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


if __name__ == "__main__":
    # pylint: disable-all

    from config import get_active_config
    from attrdict import AttrDict
    from ihs.config import get_active_config
    from ihs import create_app, db
    from collector.xml_query import XMLQuery

    conf = get_active_config()
    app = create_app()
    app.app_context().push()

    conf = get_active_config()
    endpoints = conf.endpoints
    tasks = endpoints.well_horizontal.tasks

    # tasks
    task_def = tasks.endpoint_check
    task = Task("well_horizontal", "endpoint_check", **task_def)
    to = task.options
    # print(to)
    opts = OptionMatrix(**task_def.options)

    opt_set = list(task.options)[0]

    q = XMLQuery(data_type="Well").add_filter(opt_set["api"])
    print(q.to_xml())
    print(q)
