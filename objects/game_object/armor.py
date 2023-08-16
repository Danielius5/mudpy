import contextlib
import io
from dataclasses import dataclass

from objects.game_object.base import default_dataclass_options, Item
from objects.game_object.flags import DamageType, ItemSlot


@dataclass(**default_dataclass_options)
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


@dataclass(**default_dataclass_options)
class HeadArmor(Armor):
    slots: ItemSlot = ItemSlot.HEAD


@dataclass(**default_dataclass_options)
class ChestArmor(Armor):
    slots: ItemSlot = ItemSlot.CHEST


@dataclass(**default_dataclass_options)
class LegsArmor(Armor):
    slots: ItemSlot = ItemSlot.LEGS


@dataclass(**default_dataclass_options)
class FeetArmor(Armor):
    slots: ItemSlot = ItemSlot.FEET


__all__ = ["Armor", "HeadArmor", "ChestArmor", "LegsArmor", "FeetArmor"]