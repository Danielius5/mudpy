import contextlib
import io

from game.mechanics.flags import AmmoType, DamageType, ItemSlot
from .base import go_dataclass
from .simple import Item


@go_dataclass
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


@go_dataclass
class MeleeWeapon(Weapon):
    slot: ItemSlot = ItemSlot.MAIN_HAND | ItemSlot.OFF_HAND


@go_dataclass
class RangedWeapon(Weapon):
    slot: ItemSlot = ItemSlot.RANGED
    ammo_type: AmmoType = AmmoType.NO_AMMO_TYPE


__all__ = ["Weapon", "MeleeWeapon", "RangedWeapon"]
