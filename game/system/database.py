import os
import typing

import dotenv
from pymongo.mongo_client import MongoClient

dotenv.load_dotenv()
if ENABLED := (os.environ.get("MONGO_ENABLED", "false").lower() == "true"):
    print("MongoDB Enabled. Proceeding...")
    uri = f"mongodb+srv://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@cybergunk.bwgpvsw.mongodb.net" \
          f"/?retryWrites=true&w=majority"
    client = MongoClient(uri)
    try:
        client.admin.command('ping')
    except Exception as e:
        raise Exception("There was an error connecting to the database. Please check your connection string.")
    else:
        print("DB Connection Successful. Proceeding...")
    db = client["cybergunk"]


    def clear_db():
        # this method is here for while I am testing, it will be removed later. Its job is to clear the database.
        if input("Are you sure you want to clear the database? (y/n): ") == "y":
            if input("Are you really sure? (y/n): ") == "y":
                client.drop_database("cybergunk")
                print("Database cleared.")
else:
    print("MongoDB Disabled. Proceeding...")
    import shelve


    class ShelveDB:
        def __init__(self):
            self.db = shelve.open("game.db")

        def __getitem__(self, item):
            return self.db[item]

        def __setitem__(self, key, value):
            self.db[key] = value

        def __delitem__(self, key):
            del self.db[key]

        def __contains__(self, item):
            return item in self.db

        def __iter__(self):
            return iter(self.db)


    db = ShelveDB()

GameObject = typing.TypeVar("GameObject")


def insert_game_object(
        obj: GameObject,
        /,
        cat: str = "objects"
):
    if ENABLED:
        db[cat].insert_one(obj.to_dict())
    else:
        db[cat][obj.uuid] = obj.to_dict()


def update_game_object(
        obj: GameObject,
        /,
        cat: str = "objects"
):
    if ENABLED:
        db[cat].update_one({"uuid": obj.uuid}, {"$set": obj.to_dict()})
    else:
        db[cat][obj.uuid] = obj.to_dict()


def retrieve_game_object(
        to_type: typing.Type[GameObject],
        /,
        cat: str = "objects",
        **keys
):
    if ENABLED:
        if result := db[cat].find_one(keys):
            return to_type.from_dict(result)
    else:
        if result := db[cat].get(keys.get("uuid", None)):
            return to_type.from_dict(result)
    return None


def retrieve_game_objects(
        to_type: typing.Type[GameObject],
        /,
        cat: str = "objects",
        **keys
):
    # get the dot name aka: GameObject.Item.Weapon
    name = ".".join([to_type.__module__, to_type.__name__])
    if ENABLED:
        return [to_type.from_dict(result) for result in db[cat].find(keys)]
    else:
        return [to_type.from_dict(result) for result in db[cat].values() if
                all(result.get(k, None) == v for k, v in keys.items())]


def delete_game_object(
        obj: GameObject | str,
        /,
        cat: str = "objects"
):
    if ENABLED:
        db[cat].delete_one({"uuid": obj if isinstance(obj, str) else obj.uuid})
    else:
        del db[cat][obj if isinstance(obj, str) else obj.uuid]
