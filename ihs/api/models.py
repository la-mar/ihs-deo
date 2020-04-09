from __future__ import annotations

import datetime
import logging
from typing import List, Optional, Tuple

import pandas as pd
import pytz
from mongoengine.document import Document as Model  # noqa

from api.mixin import BaseMixin, ProductionMixin, WellMixin
from ihs import db

loggger = logging.getLogger(__name__)

__all__ = [
    "ChangeDeleteLog",
    "WellMasterHorizontal",
    "WellMasterVertical",
    "ProductionMasterHorizontal",
    "ProductionMasterVertical",
    "WellHorizontal",
    "WellVertical",
    "ProductionHorizontal",
    "ProductionVertical",
]

SIX_HOURS = 6
TWO_DAYS = 48
ONE_WEEK = 168


class ChangeDeleteLog(db.Document, BaseMixin):
    meta = {"collection": "change_delete_log", "ordering": ["processed_at"]}
    sequence = db.LongField(primary_key=True)  # bigint
    date = db.DateTimeField()
    reason_code = db.IntField()
    source = db.StringField()
    uwi = db.StringField(null=True)
    new_uwi = db.StringField(null=True)
    reference_uwi = db.StringField(null=True)
    remark = db.StringField(null=True)
    active_code = db.StringField(null=True)
    proprietary = db.StringField(null=True)
    processed = db.BooleanField(default=False)
    processed_at = db.DateTimeField(null=True)
    last_update_at = db.DateTimeField(default=datetime.datetime.now)

    @classmethod
    def max_sequence(cls) -> Optional[int]:
        result = cls.objects.order_by("-sequence").first()
        if result:
            return result.sequence
        else:
            return None

    @classmethod
    def max_date(cls) -> Optional[datetime.datetime]:
        result = cls.objects.order_by("-date").first()
        if result:
            return result.date
        else:
            return None

    @classmethod
    def unprocessed(cls) -> List:
        return cls.objects(processed=False)


class County(db.Document, BaseMixin):
    meta = {"collection": "counties", "ordering": ["name"]}
    name = db.StringField(primary_key=True)
    county_code = db.StringField()
    state_code = db.StringField()
    well_v_last_run = db.DateTimeField(null=True)
    well_h_last_run = db.DateTimeField(null=True)
    prod_v_last_run = db.DateTimeField(null=True)
    prod_h_last_run = db.DateTimeField(null=True)
    well_v_ids_last_run = db.DateTimeField(null=True)
    well_h_ids_last_run = db.DateTimeField(null=True)
    prod_v_ids_last_run = db.DateTimeField(null=True)
    prod_h_ids_last_run = db.DateTimeField(null=True)

    @staticmethod
    def _is_ready(last_run: Optional[datetime.datetime], cooldown_hours: int):
        if last_run:
            threshold = datetime.datetime.utcnow() - datetime.timedelta(
                hours=cooldown_hours
            )
            return last_run < threshold
        else:
            return True

    @classmethod
    def next_available(
        cls, attr: str
    ) -> Tuple[County, str, Optional[datetime.datetime], bool, int]:
        "Get the properties describing the next available execution time of the given attribute"

        valid_attrs = [
            "well_h_last_run",
            "well_v_last_run",
            "prod_h_last_run",
            "prod_v_last_run",
            "well_v_ids_last_run",
            "well_h_ids_last_run",
            "prod_v_ids_last_run",
            "prod_h_ids_last_run",
        ]
        if attr not in valid_attrs:
            raise ValueError(f"invalid attribute: attr must be one of {valid_attrs}")

        if attr in ["well_h_last_run", "prod_h_last_run"]:
            cooldown = TWO_DAYS
        elif "_ids_" in attr:
            cooldown = SIX_HOURS
        else:
            cooldown = ONE_WEEK

        county_obj = County.objects.order_by(attr).first()
        last_run: Optional[datetime.datetime] = county_obj[attr]
        is_ready = cls._is_ready(last_run, cooldown)
        last_run_aware: Optional[datetime.datetime] = None
        if last_run:
            last_run_aware = pytz.utc.localize(last_run)
        return county_obj, attr, last_run_aware, is_ready, cooldown

    @classmethod
    def as_df(cls):
        return pd.DataFrame([x._data for x in cls.objects.all()]).set_index("name")


class WellMasterHorizontal(db.Document, BaseMixin):
    meta = {"collection": "well_master_horizontal", "ordering": ["-last_update_at"]}
    name = db.StringField(primary_key=True)
    ids = db.ListField(default=list)
    count = db.IntField(required=True, default=0)
    last_update_at = db.DateTimeField(default=datetime.datetime.now)
    ihs_last_update_date = db.DateTimeField(null=True)

    @classmethod
    def as_df(cls):
        return pd.DataFrame([x._data for x in cls.objects.all()]).set_index("name")


class WellMasterVertical(db.Document, BaseMixin):
    meta = {"collection": "well_master_vertical", "ordering": ["-last_update_at"]}
    name = db.StringField(primary_key=True)
    ids = db.ListField(default=list)
    count = db.IntField(required=True, default=0)
    last_update_at = db.DateTimeField(default=datetime.datetime.now)
    ihs_last_update_date = db.DateTimeField(null=True)

    @classmethod
    def as_df(cls):
        return pd.DataFrame([x._data for x in cls.objects.all()]).set_index("name")


class ProductionMasterHorizontal(db.Document, BaseMixin):
    meta = {
        "collection": "production_master_horizontal",
        "ordering": ["-last_update_at"],
    }
    name = db.StringField(primary_key=True)
    ids = db.ListField(default=list)
    count = db.IntField(required=True, default=0)
    last_update_at = db.DateTimeField(default=datetime.datetime.now)
    ihs_last_update_date = db.DateTimeField(null=True)

    @classmethod
    def as_df(cls):
        return pd.DataFrame([x._data for x in cls.objects.all()]).set_index("name")


class ProductionMasterVertical(db.Document, BaseMixin):
    meta = {
        "collection": "production_master_vertical",
        "ordering": ["-last_update_at"],
    }
    name = db.StringField(primary_key=True)
    ids = db.ListField(default=list)
    count = db.IntField(required=True, default=0)
    last_update_at = db.DateTimeField(default=datetime.datetime.now)
    ihs_last_update_date = db.DateTimeField(null=True)

    @classmethod
    def as_df(cls):
        return pd.DataFrame([x._data for x in cls.objects.all()]).set_index("name")


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
    import random

    app = create_app()
    app.app_context().push()

    obj = WellMasterHorizontal.objects(name="tx-upton").get()

    api14s = random.choices(obj.ids, k=100)

    prod_obj = ProductionMasterHorizontal.objects(name="tx-upton").get()

    # prod_ids = random.choices(prod_obj.ids, k=1000)

    print(prod_obj.ids)
    print(obj.ids)

# if __name__ == "__main__":
#     from ihs import create_app
#     from config import get_active_config
#     from api.helpers import paginate
#     import api.schema as schemas

#     app = create_app()
#     app.app_context().push()
#     conf = get_active_config()

#     model = ProductionMasterHorizontal
# api14 = "42461409160000"
# api14s = ["42461409160000", "42461009720100"]
# m = model.objects.get(api14=api14)  # pylint: disable=no-member

# # vertical = "42383362060000"``
# x = model.get(api14=api14)[0]
# dir(x)
# x.production_header
# m = model.get()
# objs = model.objects.only()
# [obj.id for obj in objs]
# m = model.get(api14__in=api14s, paginate=True, page=1, per_page=25)
# m = model.get(
#     ihs_last_update_date__gte="2019-12-01", paginate=True, page=1, per_page=25
# )

# dir(m)

# s = schemas.WellHeaderSchema(many=True)
# s.dump(m.items)

# county = County.next_prod_h()
# county._data
# offset = datetime.datetime.utcnow() - datetime.timedelta(days=1)
# county.prod_h_last_run = offset
# county.save()

# upton.prod_h_last_run = None
# upton.save()
