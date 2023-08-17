from game.mechanics.flags import AmmoType
from .simple import Item
from ..system.utils import go_dataclass


@go_dataclass
class Consumable(Item):
    perishable: bool = False
    decay_rate: float = 0.0
    decay_time: float = 0.0


@go_dataclass
class Pharmaceutical(Consumable):
    pass


@go_dataclass
class Food(Consumable):
    pass


@go_dataclass
class Drink(Consumable):
    pass


@go_dataclass
class Ammo(Consumable):
    ammo_type: AmmoType = AmmoType.NO_AMMO_TYPE


__all__ = ["Consumable", "Pharmaceutical", "Food", "Drink", "Ammo"]
