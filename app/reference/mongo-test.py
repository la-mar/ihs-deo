import pymongo


from pymongo import MongoClient, GEO2D
import json
# username: root
# password: qEDqRwvgHH7w

client = MongoClient('mongodb://root@ec2-34-221-192-172.us-west-2.compute.amazonaws.com:27017/?authSource=admin', username = "root", password="qEDqRwvgHH7w")

db = client.test
db.collection_names(include_system_collections=False)


records = json.loads(prod.T.to_json()).values()
db.production.insert(records)

db.polygons.create_index([("loc", GEO2D)])



