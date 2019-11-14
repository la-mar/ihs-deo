import mongoengine as me


class Well(me.DynamicDocument):
    meta = {"collection": "well", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField(unique=True)
    api10 = me.StringField()
    last_update = me.DateTimeField()


class Production(me.DynamicDocument):
    meta = {"collection": "production", "ordering": ["-last_update"]}
    identification = me.StringField(primary_key=True)
    api14 = me.StringField(unique=True)
    api10 = me.StringField()
    last_update = me.DateTimeField()


# class WellHeader(me.DynamicDocument):
#     meta = {"collection": "well_header", "ordering": ["-last_update"]}
#     uwi = me.StringField(primary_key=True)
#     api14 = me.StringField(unique=True)
#     last_update = me.DateTimeField()


# class WellLocation(me.DynamicDocument):
#     meta = {"collection": "well_location", "ordering": ["-last_update"]}
#     uwi = me.StringField(primary_key=True)
#     api14 = me.StringField(unique=True)
#     last_update = me.DateTimeField()


# class WellDrilling(me.DynamicDocument):
#     meta = {"collection": "well_drilling", "ordering": ["-last_update"]}
#     uwi = me.StringField(primary_key=True)
#     api14 = me.StringField(unique=True)
#     last_update = me.DateTimeField()


# class WellMechanical(me.DynamicDocument):
#     meta = {"collection": "well_mechanical", "ordering": ["-last_update"]}
#     uwi = me.StringField(primary_key=True)
#     api14 = me.StringField(unique=True)
#     last_update = me.DateTimeField()


# class WellGeology(me.DynamicDocument):
#     meta = {"collection": "well_geology", "ordering": ["-last_update"]}
#     uwi = me.StringField(primary_key=True)
#     api14 = me.StringField(unique=True)
#     last_update = me.DateTimeField()


# class WellGeophysics(me.DynamicDocument):
#     meta = {"collection": "well_geophysics", "ordering": ["-last_update"]}
#     uwi = me.StringField(primary_key=True)
#     api14 = me.StringField(unique=True)
#     last_update = me.DateTimeField()


# class WellEngineering(me.DynamicDocument):
#     meta = {"collection": "well_engineering", "ordering": ["-last_update"]}
#     uwi = me.StringField(primary_key=True)
#     api14 = me.StringField(unique=True)
#     last_update = me.DateTimeField()


# class WellTest(me.DynamicDocument):
#     meta = {"collection": "well_test", "ordering": ["-last_update"]}
#     uwi = me.StringField(primary_key=True)
#     api14 = me.StringField(unique=True)
#     last_update = me.DateTimeField()


# class WellTreatmentSummary(me.DynamicDocument):
#     meta = {"collection": "well_treatment_summary", "ordering": ["-last_update"]}
#     uwi = me.StringField(primary_key=True)
#     api14 = me.StringField(unique=True)
#     last_update = me.DateTimeField()


# class WellContent(me.DynamicDocument):
#     meta = {"collection": "well_content", "ordering": ["-last_update"]}
#     uwi = me.StringField(primary_key=True)
#     api14 = me.StringField(unique=True)
#     last_update = me.DateTimeField()


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
