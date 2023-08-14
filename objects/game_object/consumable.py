from dataclasses import dataclass

from objects.flags import AmmoType
from objects.game_object import Item


@dataclass
class Consumable(Item):
    perishable: bool = False
    decay_rate: float = 0.0
    decay_time: float = 0.0


@dataclass
class Pharmaceutical(Consumable):
    pass


@dataclass
class Food(Consumable):
    pass


@dataclass
class Drink(Consumable):
    pass


@dataclass
class Ammo(Consumable):
    ammo_type: AmmoType = AmmoType.NO_AMMO_TYPE


__all__ = ["Consumable", "Pharmaceutical", "Food", "Drink", "Ammo"]