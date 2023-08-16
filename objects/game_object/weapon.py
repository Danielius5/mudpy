import contextlib
import io
from dataclasses import dataclass

from objects.game_object.base import default_dataclass_options, Item
from objects.game_object.flags import AmmoType, DamageType, ItemSlot


@dataclass(**default_dataclass_options)
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


@dataclass(**default_dataclass_options)
class MeleeWeapon(Weapon):
    slot: ItemSlot = ItemSlot.MAIN_HAND | ItemSlot.OFF_HAND


@dataclass(**default_dataclass_options)
class RangedWeapon(Weapon):
    slot: ItemSlot = ItemSlot.RANGED
    ammo_type: AmmoType = AmmoType.NO_AMMO_TYPE


__all__ = ["Weapon", "MeleeWeapon", "RangedWeapon"]
