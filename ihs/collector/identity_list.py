from typing import Union, Any, List
import logging

from config import HoleDirection
from api.models import (
    WellMasterHorizontal,
    WellMasterVertical,
    ProducingEntityMasterHorizontal,
    ProducingEntityMasterVertical,
)

from collector.collector import Collector

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
            except:  # pylint: disable=bare-except
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
                "Saved %s ids to %s/%s", len(ids), self.__class__.__name__, self.key
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
                f"Invalid value for hole_direction ({hole_direction}) -- Valid options are {HoleDirection.member_names()}"
            )
        super().__init__(self.model, key)


class ProducingEntityList(IdentityList):
    def __init__(self, key: str, hole_direction: str):
        if hole_direction == HoleDirection.H.name:
            self.model = ProducingEntityMasterHorizontal
        elif hole_direction == HoleDirection.V.name:
            self.model = ProducingEntityMasterVertical
        else:
            raise ValueError(
                f"Invalid value for hole_direction ({hole_direction}) -- Valid options are {HoleDirection.member_names()}"
            )
        super().__init__(self.model, key)


if __name__ == "__main__":
    from ihs import create_app
    from api.models import WellMaster

    app = create_app()
    app.app_context().push()

    obj = IdentityList(WellMaster, "list1")
    obj.ids = ["test4", "test5", "test6"]
    print(obj)
    # list(obj)
    # obj.delete()
