from game.objects.base import BaseObject
from game.objects.mixins import BasicObject
from game.system import database
from game.system.utils import go_dataclass as ddc, hidden_field as hf, private_hidden_field as phf


@ddc
class Creature(BasicObject):
    db_category: str = phf(default = "creatures")
    name: str = hf(default = "creature")
    short_description: str = hf(default = lambda self: f"a {self.name} is here")


@ddc
class Player(BasicObject):
    db_category: str = phf(default = "players")
    player_name: str = hf(default = "Player")
    short_description: str = hf(default = lambda self: f"{self.player_name} is here")


@ddc
class Item(BasicObject):
    db_category: str = phf(default = "items")
    name: str = hf(default = "item")
    short_description: str = hf(default = lambda self: f"there is an {self.name} here")


@ddc
class WorldObject(BasicObject):
    db_category: str = phf(default = "objects")
    name: str = hf(default = "an object")
    short_description: str = hf(default = lambda self: f"{self.name} is here")


@ddc
class Room(BasicObject):
    db_category: str = phf(default = "rooms")
    name: str = hf(default = "a room")
    creatures: list[str] = hf(default_factory = list)
    players: list[str] = hf(default_factory = list)
    objects: list[str] = hf(default_factory = list)
    items: list[str] = hf(default_factory = list)
    exits: dict[str, str] = hf(default_factory = dict)

    def add(self, type, value: str | BasicObject):
        if type not in self.field_names:
            raise ValueError(f"Invalid type {type}")
        if value in getattr(self, type):
            raise ValueError(f"{value} already exists in {type}")
        if isinstance(value, BaseObject):
            value = value.uuid
        getattr(self, type).append(value)

    def remove(self, type, value: str | BasicObject):
        if type not in self.field_names:
            raise ValueError(f"Invalid type {type}")
        if isinstance(value, BaseObject):
            value = value.uuid
        getattr(self, type).remove(value)

    def short_description(self):
        return f"You are in {self.name}."

    def long_description(self):
        output = f"{self.short_description()}\n"
        for attr in ("creatures", "players", "objects", "items"):
            if (items := getattr(self, attr)):
                output += f"There are {len(items)} {attr} here.\n"
                for item in items:
                    item_object = BasicObject.from_db(cat = attr, uuid = item)
                    output += f"\t{item_object.inspect()}\n"
        if self.exits:
            output += f" There are {len(self.exits)} exits here.\n"
            for exit in self.exits:
                output += f"\t{exit}\n"
        return output


if __name__ == '__main__':
    room = Room()
    room.save()

    creature = Creature()
    creature.save()

    player = Player()
    player.save()

    item = Item()
    item.save()

    room.add("creatures", creature)
    room.add("items", item)
    room.add("players", player)
    print(room.interact("inspect", "long_description"))

    player.delete()
    creature.delete()
    item.delete()
    room.delete()

    database.clear_db()
