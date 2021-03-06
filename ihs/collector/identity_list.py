import logging
from typing import Any, List, Union

from api.models import (
    ProductionMasterHorizontal,
    ProductionMasterVertical,
    WellMasterHorizontal,
    WellMasterVertical,
)
from collector.collector import Collector
from config import HoleDirection

logger = logging.getLogger(__name__)


class IdentityList:

    _ids = None

    def __init__(self, model: Any, key: str):
        self.collector = Collector(model)
        self.model = model
        self.key = key

    def __repr__(self):
        return f"{self.__class__.__name__}/{self.key}: {len(self)} ids"

    def __len__(self):
        return len(self.ids)

    def __iter__(self):
        for i in self.ids:
            yield i

    @property
    def ids(self) -> List[str]:
        if not self._ids:
            try:
                self._ids = self.model.objects(name=self.key)[0].ids
            except Exception:
                self._ids = []
        return self._ids

    @ids.setter
    def ids(self, ids: Union[List[str], bytes], sep: str = "\n"):
        if isinstance(ids, bytes):
            self._set_ids_from_bytes(ids, sep=sep)
        else:
            self._set_ids(ids)

    def _set_ids(self, ids: list):
        if ids:
            ids = [x for x in ids if x != ""]  # drop trailing empties
            self.collector.save({"name": self.key, "count": len(ids), "ids": ids})
            logger.info(
                "Saved %s ids to %s/%s", len(ids), self.model.__name__, self.key
            )

    def _set_ids_from_bytes(self, ids: bytes, sep: str = "\n"):
        self._set_ids(ids=ids.decode().split(sep))

    def delete(self):
        self.model.objects(name=self.key).delete()
        self.ids = []


class WellList(IdentityList):
    def __init__(self, key: str, hole_direction: str):
        if hole_direction == HoleDirection.H.name:
            self.model = WellMasterHorizontal
        elif hole_direction == HoleDirection.V.name:
            self.model = WellMasterVertical
        else:
            raise ValueError(
                f"Invalid value for hole_direction ({hole_direction}) -- Valid options are {HoleDirection.member_names()}"  # noqa
            )
        super().__init__(self.model, key)


class ProductionList(IdentityList):
    def __init__(self, key: str, hole_direction: str):
        if hole_direction == HoleDirection.H.name:
            self.model = ProductionMasterHorizontal
        elif hole_direction == HoleDirection.V.name:
            self.model = ProductionMasterVertical
        else:
            raise ValueError(
                f"Invalid value for hole_direction ({hole_direction}) -- Valid options are {HoleDirection.member_names()}"  # noqa
            )
        super().__init__(self.model, key)
