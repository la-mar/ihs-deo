from mongoengine import connect
from ihs.config import get_active_config
from ihs import create_app, db

conf = get_active_config()
app = create_app()
app.app_context().push()


db.connection.list_database_names()


# conf = get_active_config()
# auth = conf.database_params

# uuidRepresentation = "standard"
# auth.pop("driver")
# client = connect(name="test", **auth)
# client = connect(name="test", host=conf.database_uri())
# client
# db.list_database_names()
# db = client.ihs

# have to manually auth against admin when not using uri with mongoengine
# db.authenticate(
#     name=auth.get("username"),
#     password=auth.get("password"),
#     source=auth.get("authentication_source"),
# )


# db.list_collection_names()

# db.name
# dir(db)
# db.get_collection("test")


# records = json.loads(prod.T.to_json()).values()
# db.production.insert(records)

# db.polygons.create_index([("loc", GEO2D)])


# from pymongo import MongoClient

# auth.pop("authentication_source")
# auth.pop("db")
# client = MongoClient(**auth)
