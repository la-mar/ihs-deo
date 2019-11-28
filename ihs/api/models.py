from typing import no_type_check, List, Dict
import functools
import datetime
import mongoengine as me

from util.deco import classproperty
from util import query_dict
from util.geo import CoordinateTransformer
from config import get_active_config

conf = get_active_config()

projector = CoordinateTransformer(conf.DEFAULT_PROJECTION)


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


class WellMixin(BaseMixin):
    @property
    def well_locations(self):
        locs = {}
        loc_type_map = {
            "shl": ["surface", "shl"],
            "bhl": ["actual bottom hole", "abhl"],
            "pbhl": ["proposed bottom hole", "pbhl"],
        }

        for loc in self.location:
            get = functools.partial(query_dict, data=loc)
            type_name = loc.get("type_name", "").lower()
            type_code = loc.get("type_code", "").lower()
            datum = get("geographic.datum.code")

            for loc_name, loc_aliases in loc_type_map.items():
                if type_name in loc_aliases or type_code in loc_aliases:
                    lon, lat, crs = projector.transform(
                        x=get("geographic.longitude"),
                        y=get("geographic.latitude"),
                        crs=datum.lower(),
                    )
                    locs[loc_name] = {
                        "lon": lon,
                        "lat": lat,
                        "crs": crs,
                        "block": get("texas.block.number"),
                        "section": get("texas.section.number"),
                        "abstract": get("texas.abstract"),
                        "survey": get("texas.survey"),
                        "metes_bounds": get("texas.footage.concatenated"),
                    }
        return locs

    @property
    def active_survey(self):

        shl_lat = query_dict("shl.lat", self.well_locations)
        shl_lon = query_dict("shl.lon", self.well_locations)

        header = {}
        points = []
        data = {}
        if hasattr(self, "surveys"):
            data = self["surveys"].get("borehole")

        get = functools.partial(query_dict, data=data)

        header["survey_type"] = get("type_code")
        header["survey_method"] = get("header.methods.survey.code")
        header["survey_end_date"] = get("header.dates.end.standard")
        header["survey_top"] = get("header.depths.top.value")
        header["survey_top_uom"] = get("header.depths.top.uom")
        header["survey_base"] = get("header.depths.base.value")
        header["survey_base_uom"] = get("header.depths.base.uom")

        for point in get("point"):
            pt = {}
            pt["md"] = query_dict("depths.measured.value", point)
            pt["md_uom"] = query_dict("depths.measured.uom", point)
            pt["tvd"] = query_dict("depths.true_vertical.value", point)
            pt["tvd_uom"] = query_dict("depths.true_vertical.uom", point)
            pt["lon"] = shl_lon or 0 + query_dict("delta.longitude", point) or 0
            pt["lat"] = shl_lat or 0 + query_dict("delta.latitude", point) or 0
            points.append(pt)

        header["points"] = points

        return header


class ProductionMixin(BaseMixin):
    pass


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
    m.active_survey.keys()
