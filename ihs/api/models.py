import datetime
import mongoengine as me


class WellMasterHorizontal(me.Document):
    meta = {"collection": "well_master_horizontal", "ordering": ["-last_update"]}
    name = me.StringField(primary_key=True)
    ids = me.ListField()
    count = me.IntField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class WellMasterVertical(me.Document):
    meta = {"collection": "well_master_vertical", "ordering": ["-last_update"]}
    name = me.StringField(primary_key=True)
    ids = me.ListField()
    count = me.IntField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class ProducingEntityMasterHorizontal(me.Document):
    meta = {
        "collection": "producing_entity_master_horizontal",
        "ordering": ["-last_update"],
    }
    identification = me.StringField(primary_key=True)
    count = me.IntField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class ProducingEntityMasterVertical(me.Document):
    meta = {
        "collection": "producing_entity_master_vertical",
        "ordering": ["-last_update"],
    }
    identification = me.StringField(primary_key=True)
    count = me.IntField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class WellHorizontal(me.DynamicDocument):
    meta = {"collection": "well_horizontal", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField(unique=True)
    api10 = me.StringField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class WellVertical(me.DynamicDocument):
    meta = {"collection": "well_vertical", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField(unique=True)
    api10 = me.StringField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class ProductionHorizontal(me.DynamicDocument):
    meta = {"collection": "production_horizontal", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField(unique=True)
    api10 = me.StringField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


class ProductionVertical(me.DynamicDocument):
    meta = {"collection": "production_vertical", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField(unique=True)
    api10 = me.StringField()
    last_update = me.DateTimeField(default=datetime.datetime.now)


if __name__ == "__main__":
    from ihs.config import get_active_config
    from ihs import create_app, db

    conf = get_active_config()
    app = create_app()
    app.app_context().push()

    well = Well(api14="12345678901234")
    well.save()

    WELL_COLLECTIONS = [
        "well_header",
        "well_location",
        "well_drilling",
        "well_mechanical",
        "well_geology",
        "well_geophysics",
        "well_engineering",
        "well_tests",
        "well_treatment_summary",
        "well_content",
    ]
