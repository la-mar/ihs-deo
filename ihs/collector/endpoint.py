from __future__ import annotations

import logging
from pydoc import locate
from typing import Any, Dict, Generic, ItemsView, List, Tuple, TypeVar, Union

from attrdict import AttrDict

from api.models import *
from collector.task import Task
import yaml

logger = logging.getLogger(__name__)

M = TypeVar("M")
Column = TypeVar("Column")


class Model(Generic[M]):
    pass


class Endpoint(object):
    def __init__(
        self,
        name: str,
        model: str,
        version: str = None,
        path: str = None,
        mappings: Dict[str, str] = None,
        url_params: List[str] = None,
        exclude: List[str] = None,
        depends_on: Dict[str, str] = None,
        options: dict = None,
        normalize: bool = False,
        updated_column: str = "updated_at",
        enabled: bool = True,
        tasks: dict = None,
        propagate_to_task: bool = True,
        **kwargs,
    ):

        self.name = name
        self.version = version
        self.path = path
        self.mappings = AttrDict(mappings or {})
        self.model_name = model
        self._model: Union[Model, None] = None
        self.updated_column = updated_column
        self.url_params = url_params
        self.exclude = exclude or []
        self._dependency_map = depends_on or {}
        self.normalize = normalize
        self.options = options or {}
        self.enabled = enabled
        self.propagate_to_task = propagate_to_task
        self.tasks: Dict[str, Task] = {}
        self.add_tasks((tasks or {}).items())

    def __repr__(self):
        return f"Endpoint: {self.version}/{self.name}"

    def __iter__(self):
        attrs = [x for x in dir(self) if not x.startswith("_")]
        for a in attrs:
            yield a, getattr(self, a)

    @property
    def model(self) -> Union[Model, None]:
        if self._model is None:
            self._model = self.locate_model(self.model_name)
        return self._model

    def locate_model(self, model_name: str) -> Model:
        model: Any = None
        try:
            # try to import dotted model name. ex: api.models.MyModel
            model = locate(model_name)
            if model is None:
                raise ModuleNotFoundError
            logger.debug(f"Found model: {model_name}")
        except ModuleNotFoundError:
            logger.debug(
                f"Failed to import module '{model_name}' from project directory"
            )
            try:
                # try to import model from global namespace
                model = globals()[model_name]
                logger.debug(f"Model '{model_name}' found in global namespace")
            except (ModuleNotFoundError, KeyError):
                raise ModuleNotFoundError(
                    f"No module named '{model_name}' found in project or global namespace"
                )

        return model

    def add_task(self, task_name: str, **kwargs):
        if self.propagate_to_task:
            kwargs["options"] = {**self.options, **kwargs.get("options", {})}

        self.tasks[task_name] = Task(
            model_name=self.model_name,
            task_name=task_name,
            endpoint_name=self.name,
            **kwargs,
        )

    def add_tasks(self, task_defs: Union[ItemsView, List[Tuple[str, dict]]]):
        for name, task_def in task_defs:
            self.add_task(task_name=name, **task_def)

    @staticmethod
    def load_from_config(
        app_config: object, load_disabled: bool = False
    ) -> Dict[str, Endpoint]:
        endpoints: dict = {}
        try:
            endpoints = app_config.endpoints  # type: ignore
        except AttributeError:
            raise AttributeError("Config object has no attribute 'endpoints'")

        loaded: Dict[str, Endpoint] = {}
        for ep in endpoints.items():
            try:
                new = Endpoint(name=ep[0], **ep[1])
                if new.enabled or load_disabled:
                    loaded[ep[0]] = new
            except Exception as e:
                logger.error(f"Failed to create endpoint ({ep[0]}) -> {e}")
        return loaded

    @staticmethod
    def from_dict(name: str, data: dict):
        return Endpoint(name, **data)

    @staticmethod
    def from_yaml(path: str, load_disabled: bool = False, key: str = "endpoints"):
        endpoints = {}
        with open(path) as f:
            endpoints = yaml.safe_load(f)

        if key:
            endpoints = endpoints[key]

        loaded: Dict[str, Endpoint] = {}
        for ep in endpoints.items():
            try:
                new = Endpoint(name=ep[0], **ep[1])
                if new.enabled or load_disabled:
                    loaded[ep[0]] = new
            except Exception as e:
                logger.error(f"Failed to create endpoint ({ep[0]}) -> {e}")
        return loaded


if __name__ == "__main__":
    from ihs import create_app

    app = create_app()
    app.app_context().push()

    path = "tests/data/collector.yaml"
    load_disabled = False
    endpoints = Endpoint.from_yaml(path)

    list(endpoints.items())[0]
    opts = list(endpoints["well_horizontal"].tasks["sync"].options)
    opts[0]
    # from api.models import County
