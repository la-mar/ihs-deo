from typing import no_type_check, List, Dict
from collections import OrderedDict
import functools
import datetime
import logging
import mongoengine as me

from api.mixin import BaseMixin, WellMixin, ProductionMixin


loggger = logging.getLogger(__name__)


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


class WellHorizontal(me.DynamicDocument, WellMixin):
    meta = {"collection": "well_horizontal", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField(unique=True)
    api10 = me.StringField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class WellVertical(me.DynamicDocument, WellMixin):
    meta = {"collection": "well_vertical", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField(unique=True)
    api10 = me.StringField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class ProductionHorizontal(me.DynamicDocument, ProductionMixin):
    meta = {"collection": "production_horizontal", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField()
    api10 = me.StringField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class ProductionVertical(me.DynamicDocument, ProductionMixin):
    meta = {"collection": "production_vertical", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField()
    api10 = me.StringField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


if __name__ == "__main__":
    from ihs import create_app

    app = create_app()
    app.app_context().push()
    conf = get_active_config()

    model = WellHorizontal
    api14 = "42461409160000"
    m = model.objects.get(api14=api14)  # pylint: disable=no-member

    # vertical = "42383362060000"
    model.get(api14=api14)

