import os
import typing

import dotenv
from pymongo.mongo_client import MongoClient

dotenv.load_dotenv()
if not (ENABLED := (os.environ.get("MONGO_ENABLED", "false").lower() == "true")):
    print("MongoDB Disabled. Proceeding...")
else:
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
    if os.environ.get("MONGO_ALLOW_WIPING_DB", "false").lower() == "true":

        def clear_db():
            if input("Are you sure you want to clear the database? (y/n): ") == "y":
                if input("Are you really sure? (y/n): ") == "y":
                    client.drop_database("cybergunk")
                    print("Database cleared.")

    BaseObject = typing.TypeVar("BaseObject")


    def insert_game_object(
            obj: BaseObject,
            /,
            cat: str = "objects"
    ):
        db[cat].insert_one(obj.to_dict(show_private = True))


    def update_game_object(
            obj: BaseObject,
            /,
            cat: str = "objects"
    ):
        db[cat].update_one({"uuid": obj.uuid}, {"$set": obj.to_dict(show_private = True)})


    def retrieve_game_object(
            to_type: typing.Type[BaseObject],
            /,
            cat: str = "objects",
            **keys
    ):
        if result := db[cat].find_one(keys):
            return to_type.from_dict(result)
        return None


    def retrieve_game_objects(
            to_type: typing.Type[BaseObject],
            /,
            cat: str = "objects",
            **keys
    ):
        return [to_type.from_dict(result) for result in db[cat].find(keys)]


    def delete_game_object(
            obj: BaseObject | str,
            /,
            cat: str = "objects"
    ):
        db[cat].delete_one({"uuid": obj if isinstance(obj, str) else obj.uuid})
