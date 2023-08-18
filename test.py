from pprint import pprint

from game.objects.base import BaseObject, ObjectFactory
from game.objects.mixins import DBSerializable, GarbageCollected, Inspectable
from game.system.utils import go_dataclass as ddc, hidden_field as hf, private_hidden_field as phf


@ddc
class Room(BaseObject, GarbageCollected, Inspectable, DBSerializable):
    db_category: str = phf(default = "rooms")
    name: str = hf(default = "A room")


RoomFactory: ObjectFactory[Room] = Room.factory()
LargeRoomFactory: ObjectFactory[Room] = RoomFactory.bind(name = "a large room")
SmallRoomFactory: ObjectFactory[Room] = RoomFactory.bind(name = "a small room")

room = RoomFactory.create()
large_room = LargeRoomFactory.create()
small_room = SmallRoomFactory.create()

room_dict = room.to_dict(show_private = True)
room_dict_public = room.to_dict()

pprint(room_dict)
pprint(room_dict_public)
