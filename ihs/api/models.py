from typing import no_type_check, List, Dict
import datetime
import mongoengine as me

from util.deco import classproperty


class BaseMixin:
    @classproperty
    @no_type_check
    def primary_keys(self) -> List[str]:
        return [name for name, column in self._fields.items() if column.primary_key]

    def primary_key_values(self) -> List[Dict]:
        pks = self.primary_keys
        data = [m for m in self.objects.only(*pks)]  # type: ignore
        unpacked = []
        for d in data:
            limited = {}
            for pk in pks:
                limited[pk] = d[pk]
            unpacked.append(limited)
        return unpacked


class WellMasterHorizontal(me.Document, BaseMixin):
    meta = {"collection": "well_master_horizontal", "ordering": ["-last_update"]}
    name = me.StringField(primary_key=True)
    ids = me.ListField()
    count = me.IntField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class WellMasterVertical(me.Document, BaseMixin):
    meta = {"collection": "well_master_vertical", "ordering": ["-last_update"]}
    name = me.StringField(primary_key=True)
    ids = me.ListField()
    count = me.IntField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class ProductionMasterHorizontal(me.Document, BaseMixin):
    meta = {
        "collection": "production_master_horizontal",
        "ordering": ["-last_update"],
    }
    name = me.StringField(primary_key=True)
    ids = me.ListField()
    count = me.IntField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class ProductionMasterVertical(me.Document, BaseMixin):
    meta = {
        "collection": "production_master_vertical",
        "ordering": ["-last_update"],
    }
    name = me.StringField(primary_key=True)
    ids = me.ListField()
    count = me.IntField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class WellHorizontal(me.DynamicDocument, BaseMixin):
    meta = {"collection": "well_horizontal", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField(unique=True)
    api10 = me.StringField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class WellVertical(me.DynamicDocument, BaseMixin):
    meta = {"collection": "well_vertical", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField(unique=True)
    api10 = me.StringField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class ProductionHorizontal(me.DynamicDocument, BaseMixin):
    meta = {"collection": "production_horizontal", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField()
    api10 = me.StringField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class ProductionVertical(me.DynamicDocument, BaseMixin):
    meta = {"collection": "production_vertical", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField()
    api10 = me.StringField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


if __name__ == "__main__":
    from ihs.config import get_active_config
    from ihs import create_app, db

    conf = get_active_config()
    app = create_app()
    app.app_context().push()

    obj = WellMasterHorizontal.objects()[0]
    obj.ids
