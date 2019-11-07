
from pymongo import MongoClient, GEO2D

import app


from .version import __project__
from app.settings import *



client = MongoClient(DATABASE_URI)

db = client.driftwood
db.collection_names()
db.name
dir(db)
db.get_collection('test')







# records = json.loads(prod.T.to_json()).values()
# db.production.insert(records)

# db.polygons.create_index([("loc", GEO2D)])



