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

# * seed counties model
coll = Collector(County)
coll.save(counties, replace=False)

# * replicate county definitions to well/prod master lists where missing
county_name_only = [{"name": d["name"]} for d in counties]
for model in [
    WellMasterHorizontal,
    WellMasterVertical,
    ProductionMasterHorizontal,
    ProductionMasterVertical,
]:
    existing = [x._data["name"] for x in model.objects()]
    for county in county_name_only:

        if county["name"] not in existing:
            i = model(**county)
            i.save()
            print(f"({model.__name__}) added {county['name']}")


print("")
