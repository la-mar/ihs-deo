import datetime
import logging

from api.mixin import BaseMixin, WellMixin, ProductionMixin
from ihs import db


loggger = logging.getLogger(__name__)


class WellMasterHorizontal(db.Document, BaseMixin):
    meta = {"collection": "well_master_horizontal", "ordering": ["-last_update_at"]}
    name = db.StringField(primary_key=True)
    ids = db.ListField()
    count = db.IntField()
    last_update_at = db.DateTimeField(default=datetime.datetime.now)
    ihs_last_update_date = db.DateTimeField()


class WellMasterVertical(db.Document, BaseMixin):
    meta = {"collection": "well_master_vertical", "ordering": ["-last_update_at"]}
    name = db.StringField(primary_key=True)
    ids = db.ListField()
    count = db.IntField()
    last_update_at = db.DateTimeField(default=datetime.datetime.now)
    ihs_last_update_date = db.DateTimeField()


class ProductionMasterHorizontal(db.Document, BaseMixin):
    meta = {
        "collection": "production_master_horizontal",
        "ordering": ["-last_update_at"],
    }
    name = db.StringField(primary_key=True)
    ids = db.ListField()
    count = db.IntField()
    last_update_at = db.DateTimeField(default=datetime.datetime.now)
    ihs_last_update_date = db.DateTimeField()


class ProductionMasterVertical(db.Document, BaseMixin):
    meta = {
        "collection": "production_master_vertical",
        "ordering": ["-last_update_at"],
    }
    name = db.StringField(primary_key=True)
    ids = db.ListField()
    count = db.IntField()
    last_update_at = db.DateTimeField(default=datetime.datetime.now)
    ihs_last_update_date = db.DateTimeField()


class WellHorizontal(db.DynamicDocument, WellMixin):
    meta = {"collection": "well_horizontal", "ordering": ["-last_update_at"]}
    identification = db.StringField(primary_key=True)
    api14 = db.StringField(unique=True)
    api10 = db.StringField()
    last_update_at = db.DateTimeField(default=datetime.datetime.now)
    ihs_last_update_date = db.DateTimeField()


class WellVertical(db.DynamicDocument, WellMixin):
    meta = {"collection": "well_vertical", "ordering": ["-last_update_at"]}
    identification = db.StringField(primary_key=True)
    api14 = db.StringField(unique=True)
    api10 = db.StringField()
    last_update_at = db.DateTimeField(default=datetime.datetime.now)
    ihs_last_update_date = db.DateTimeField()


class ProductionHorizontal(db.DynamicDocument, ProductionMixin):
    meta = {"collection": "production_horizontal", "ordering": ["-last_update_at"]}
    identification = db.StringField(primary_key=True)
    api10 = db.StringField()
    last_update_at = db.DateTimeField(default=datetime.datetime.now)
    ihs_last_update_date = db.DateTimeField()


class ProductionVertical(db.DynamicDocument, ProductionMixin):
    meta = {"collection": "production_vertical", "ordering": ["-last_update_at"]}
    identification = db.StringField(primary_key=True)
    api10 = db.StringField()
    last_update_at = db.DateTimeField(default=datetime.datetime.now)
    ihs_last_update_date = db.DateTimeField()


if __name__ == "__main__":
    from ihs import create_app
    from config import get_active_config

    app = create_app()
    app.app_context().push()
    conf = get_active_config()

    model = ProductionHorizontal
    api14 = "42461409160000"
    m = model.objects.get(api14=api14)  # pylint: disable=no-member

    # vertical = "42383362060000"
    x = model.get(api14=api14)[0]
    dir(x)
    x.production_header

    x = model.get(paginate=True, ihs_last_update_date__gte="2020-01-01")

