import contextlib
import io
from dataclasses import dataclass

from objects.flags import AmmoType, DamageType, ItemSlot
from objects.game_object.base import Item


@dataclass
class Weapon(Item):
    damage: int = 0
    damage_type: DamageType = DamageType.NO_DAMAGE_TYPE
    max_stack_size: int = 1

    def detailed_description(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            print(super().detailed_description().strip())
            print(f"Damage: {self.damage}")
            print(f"Damage Type: {self.damage_type}")
            return f.getvalue()


@dataclass
class MeleeWeapon(Weapon):
    slot: ItemSlot = ItemSlot.MAIN_HAND | ItemSlot.OFF_HAND


@dataclass
class RangedWeapon(Weapon):
    slot: ItemSlot = ItemSlot.RANGED
    ammo_type: AmmoType = AmmoType.NO_AMMO_TYPE


__all__ = ["Weapon", "MeleeWeapon", "RangedWeapon"]
