from api.models import County
from collector import Collector
from util import load_json


from ihs import create_app

app = create_app()
app.app_context().push()

counties = load_json("data/counties.json")
coll = Collector(County)
coll.save(counties)
