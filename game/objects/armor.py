import contextlib
import io

from game.mechanics.flags import DamageType, ItemSlot
from .base import go_dataclass
from .simple import Item


@go_dataclass
class Armor(Item):
    defense: int = 0
    defense_type: DamageType = DamageType.NO_DAMAGE_TYPE
    max_stack_size: int = 1

    def detailed_description(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            print(super().detailed_description().strip())
            print(f"Defense: {self.defense}")
            print(f"Defense Type: {self.defense_type}")
            return f.getvalue()


@go_dataclass
class HeadArmor(Armor):
    slots: ItemSlot = ItemSlot.HEAD


@go_dataclass
class ChestArmor(Armor):
    slots: ItemSlot = ItemSlot.CHEST


@go_dataclass
class LegsArmor(Armor):
    slots: ItemSlot = ItemSlot.LEGS


@go_dataclass
class FeetArmor(Armor):
    slots: ItemSlot = ItemSlot.FEET


__all__ = ["Armor", "HeadArmor", "ChestArmor", "LegsArmor", "FeetArmor"]