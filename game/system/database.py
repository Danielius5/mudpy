import os
import sched
import typing
from abc import ABC
from dataclasses import dataclass, field

import dotenv
from pymongo.mongo_client import MongoClient

dotenv.load_dotenv()

uri = f"mongodb+srv://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@cybergunk.bwgpvsw.mongodb.net" \
      f"/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["cybergunk"]
sh = sched.scheduler()


def clear_db():
    # this method is here for while I am testing, it will be removed later. Its job is to clear the database.
    if input("Are you sure you want to clear the database? (y/n): ") == "y":
        if input("Are you really sure? (y/n): ") == "y":
            client.drop_database("cybergunk")
            print("Database cleared.")


GameObject = typing.TypeVar("GameObject")


def insert_game_object(
        obj: GameObject,
        /,
        cat: str = "objects"
):
    db[cat].insert_one(obj.to_dict())


def update_game_object(
        obj: GameObject,
        /,
        cat: str = "objects"
):
    db[cat].update_one({"uuid": obj.uuid}, {"$set": obj.to_dict()})


def retrieve_game_object(
        to_type: typing.Type[GameObject],
        /,
        cat: str = "objects",
        **keys
):
    if result := db[cat].find_one(keys):
        return to_type.from_dict(result)
    return None


def retrieve_game_objects(
        to_type: typing.Type[GameObject],
        /,
        cat: str = "objects",
        **keys
):
    return [to_type.from_dict(result) for result in db[cat].find(keys)]


def delete_game_object(
        obj: GameObject | str,
        /,
        cat: str = "objects"
):
    db[cat].delete_one({"uuid": obj if isinstance(obj, str) else obj.uuid})


def wipe_game_objects(
        cat: str = "objects",
        **keys
):
    db[cat].delete_many(keys)


try:
    client.admin.command('ping')
except Exception as e:
    raise Exception("There was an error connecting to the database. Please check your connection string.")
else:
    print("DB Connection Successful. Proceeding...")


# noinspection PyArgumentList
@dataclass
class DBContainedObject(ABC):
    category: str = field(default = "objects", init = False)

    def add_to_db(self):
        insert_game_object(self, cat = self.category)

    def update_in_db(self):
        update_game_object(self, cat = self.category)

    def remove_from_db(self):
        delete_game_object(self, cat = self.category)

    @classmethod
    def from_db(cls, **kwargs):
        # noinspection PyArgumentList
        return retrieve_game_object(cls, cat = cls.category, **kwargs)

    # noinspection PyArgumentList
    @classmethod
    def from_db_all(cls, **kwargs):
        return retrieve_game_objects(cls, cat = cls.category, **kwargs)

    @classmethod
    def wipe_from_db(cls, **kwargs):
        wipe_game_objects(cat = cls.category, **kwargs)
        