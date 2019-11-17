from typing import Union, Any, List
import logging

from api.models import WellMaster, ProducingEntityMaster


logger = logging.getLogger(__name__)


class IdentityList:

    _ids = None

    def __init__(self, model: Any, key: str):
        self.model = model
        self.key = key

    def __repr__(self):
        return f"{self.__class__.__name__}: {len(self)} ids"

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
        ids = [x for x in ids if x != ""]  # drop trailing empties
        self.model(**{"name": self.key, "count": len(ids), "ids": ids}).save()

    def _set_ids_from_bytes(self, ids: bytes, sep: str = "\n"):
        self._set_ids(ids=ids.decode().split(sep))

    def delete(self):
        self.model.objects(name=self.key).delete()
        self.ids = []


class WellList(IdentityList):

    model = WellMaster

    def __init__(self, key: str):
        super().__init__(self.model, key)


class ProducingEntityList(IdentityList):

    model = ProducingEntityMaster

    def __init__(self, key: str):
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
