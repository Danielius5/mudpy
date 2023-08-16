from dataclasses import dataclass

from objects.game_object import Item
from objects.game_object.base import default_dataclass_options
from objects.game_object.flags import AmmoType


@dataclass(**default_dataclass_options)
class Consumable(Item):
    perishable: bool = False
    decay_rate: float = 0.0
    decay_time: float = 0.0


@dataclass(**default_dataclass_options)
class Pharmaceutical(Consumable):
    pass


@dataclass(**default_dataclass_options)
class Food(Consumable):
    pass


@dataclass(**default_dataclass_options)
class Drink(Consumable):
    pass


@dataclass(**default_dataclass_options)
class Ammo(Consumable):
    ammo_type: AmmoType = AmmoType.NO_AMMO_TYPE


__all__ = ["Consumable", "Pharmaceutical", "Food", "Drink", "Ammo"]