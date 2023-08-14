import contextlib
import io
from dataclasses import dataclass

from objects.flags import DamageType, ItemSlot
from objects.game_object.base import Item


@dataclass
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


@dataclass
class HeadArmor(Armor):
    slot: ItemSlot = ItemSlot.HEAD


@dataclass
class ChestArmor(Armor):
    slot: ItemSlot = ItemSlot.CHEST


@dataclass
class LegsArmor(Armor):
    slot: ItemSlot = ItemSlot.LEGS


@dataclass
class FeetArmor(Armor):
    slot: ItemSlot = ItemSlot.FEET


__all__ = ["Armor", "HeadArmor", "ChestArmor", "LegsArmor", "FeetArmor"]