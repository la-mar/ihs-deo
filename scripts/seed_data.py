from api.models import (
    County,
    WellMasterHorizontal,
    WellMasterVertical,
    ProductionMasterHorizontal,
    ProductionMasterVertical,
)
from collector import Collector
from util import load_json


from ihs import create_app
import loggers

loggers.config(10)

app = create_app()
app.app_context().push()

counties = load_json("data/counties.json")
coll = Collector(County)
coll.save(counties, replace=False)

county_name_only = [{"name": d["name"]} for d in counties]
for model in [
    WellMasterHorizontal,
    WellMasterVertical,
    ProductionMasterHorizontal,
    ProductionMasterVertical,
]:
    for county in county_name_only:
        # print(county)
        i = model(**county)  # .save()
        i.save()
    # coll = Collector(model)
    # coll.save(county_name_only, replace=False)

print("")


for model in [
    WellMasterHorizontal,
    WellMasterVertical,
    ProductionMasterHorizontal,
    ProductionMasterVertical,
]:
    for county in model.objects.all():
        if "County" in county.name:
            print(county.name)
            county.delete()
