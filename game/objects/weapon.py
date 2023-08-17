import contextlib
import io
from dataclasses import field

from .simple import Item
from ..mechanics.flags import AmmoType, DamageType, ItemSlot
from ..system.utils import go_dataclass


@go_dataclass
class Weapon(Item):
    damage: int = 0
    damage_type: DamageType = field(default = DamageType.NO_DAMAGE_TYPE, metadata = {"to_type": DamageType})
    max_stack_size: int = 1

    def detailed_description(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            print(super().detailed_description().strip())
            print(f"Damage: {self.damage}")
            print(f"Damage Type: {self.damage_type}")
            return f.getvalue()


@go_dataclass
class MeleeWeapon(Weapon):
    slot: ItemSlot = field(default = ItemSlot.MAIN_HAND | ItemSlot.OFF_HAND, metadata = {"to_type": ItemSlot})


@go_dataclass
class RangedWeapon(Weapon):
    slot: ItemSlot = field(default = ItemSlot.MAIN_HAND | ItemSlot.OFF_HAND, metadata = {"to_type": ItemSlot})
    ammo_type: AmmoType = field(default = AmmoType.NO_AMMO_TYPE, metadata = {"to_type": AmmoType})


__all__ = ["Weapon", "MeleeWeapon", "RangedWeapon"]
