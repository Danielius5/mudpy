import contextlib
import io
from dataclasses import field

from game.mechanics.flags import WorldSpaceFlavor, WorldSpaceType
from game.objects.base import go_dataclass
from .base import GameObject
from ..mechanics.flags import *


@go_dataclass
class Item(GameObject):
    name_prefix: str = field(default = "")
    name_infix: str = field(default = "")
    name_suffix: str = field(default = "")

    stack_size: int = field(default = 1)
    max_stack_size: int = field(default = 1, repr = False)
    weight: float = field(default = 0.0)
    value: int = field(default = 0)

    slots: ItemSlot = field(default = ItemSlot.NO_SLOT, metadata = {"to_type": ItemSlot}, repr = False)
    effects: Effect = field(default = Effect.NO_EFFECT, metadata = {"to_type": Effect}, repr = False)

    compare_using_name: bool = field(default = True, repr = False, init = False)

    def short_description(self):
        return self.name_infix

    def long_description(self):
        return self.name

    def detailed_description(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            print(f"Name: {' '.join([part for part in [self.name_prefix, self.name_infix, self.name_suffix] if part])}")
            if self.slots != ItemSlot.NO_SLOT:
                print(f"Slot: {self.slots}")
            if self.effects != Effect.NO_EFFECT:
                print(f"Effects: {', '.join([str(effect) for effect in Effect.get_flags(self.effects)])}")
            print(f"Stack Size: {self.stack_size}")
            print(f"Weight: {self.stack_weight}")
            print(f"Value: {self.stack_value}")
            return f.getvalue()

    @property
    def name(self):
        return f"{self.name_prefix} {self.name_infix} {self.name_suffix}".strip()

    @name.setter
    def name(self, value):
        self.prefix, self.infix, self.suffix = value

    @property
    def stack_weight(self):
        return self.weight * self.stack_size

    @property
    def stack_value(self):
        return self.value * self.stack_size

    def stack(self, other):
        if not self.allowed_actions & ObjectAction.STACK:
            return "Nothing to stack here"
        if not isinstance(other, self.__class__):
            raise ValueError("Cannot stack two different items")
        if self.compare_using_name and self.name != other.name:
            raise ValueError("Cannot stack two different items")
        if self.stack_size + other.stack_size > self.max_stack_size:
            raise ValueError("Cannot stack two items over the max stack size")
        self.stack_size += other.stack_size
        del other
        return self

    def __post_init__(self):
        if not self.name_infix:
            self.name_infix = self.__class__.__name__.title()


@go_dataclass
class Currency(Item):
    weight: float = field(default = 0.1)
    max_stack_size: int = field(default = 100_000_000)
    value: int = field(default = 1)
    slots: ItemSlot = field(default = ItemSlot.WALLET, metadata = {"to_type": ItemSlot})
    compare_using_name: bool = field(default = False)

    @property
    def name_infix(self):
        if self.stack_size > 1:
            return "Credits"
        return "Credit"

    @name_infix.setter
    def name_infix(self, value):
        pass

    @property
    def name_prefix(self):
        if self.stack_size == 1:
            return "A single"
        elif self.stack_size < 1000:
            return "A stack of"
        elif self.stack_size < 1_000_000:
            return "A large stack of"
        else:
            return "A huge stack of"

    @name_prefix.setter
    def name_prefix(self, value):
        pass


@go_dataclass
class Living(GameObject):
    name_infix: str = field(default = "")
    name_prefix: str = field(default = "")
    name_suffix: str = field(default = "")

    max_health: int = field(default = 100)
    health: int = field(default = 100)
    max_stamina: int = field(default = 100)
    stamina: int = field(default = 100)
    max_thirst: int = field(default = 100)
    thirst: int = field(default = 100)
    max_hunger: int = field(default = 100)
    hunger: int = field(default = 100)
    max_energy: int = field(default = 100)
    energy: int = field(default = 100)

    allowed_actions: ObjectAction = field(
            default = ObjectAction.INSPECT,
            metadata = {"to_type": ObjectAction}
    )

    def short_description(self):
        return self.name_infix

    def long_description(self):
        return self.name

    def detailed_description(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            print(f"Name: {' '.join([part for part in [self.name_prefix, self.name_infix, self.name_suffix] if part])}")
            print(f"Health: {self.health}/{self.max_health}")
            print(f"Stamina: {self.stamina}/{self.max_stamina}")
            print(f"Thirst: {self.thirst}/{self.max_thirst}")
            print(f"Hunger: {self.hunger}/{self.max_hunger}")
            print(f"Energy: {self.energy}/{self.max_energy}")
            return f.getvalue()

    @property
    def name(self):
        return f"{self.name_prefix} {self.name_infix} {self.name_suffix}".strip()

    @name.setter
    def name(self, value):
        self.prefix, self.infix, self.suffix = value


@go_dataclass
class WorldObject(GameObject):
    pass


@go_dataclass
class WorldSpace(GameObject):
    world_space_name: str = field(default = "")
    creatures: list[Living] = field(default_factory = list)
    items: list[Item] = field(default_factory = list)
    world_objects: list[WorldObject] = field(default_factory = list)
    world_space_type: WorldSpaceType = field(
            default = WorldSpaceType.ROOM,
            metadata = {"to_type": WorldSpaceType}
    )
    world_space_flavor: WorldSpaceFlavor = field(
            default = WorldSpaceFlavor.NO_FLAVOR,
            metadata = {"to_type": WorldSpaceFlavor}
    )
    allowed_actions: ObjectAction = field(
            default = ObjectAction.INSPECT,
            metadata = {"to_type": ObjectAction}
    )

    def short_description(self):
        return f"A {self.world_space_type.name.lower()}"

    def long_description(self):
        if self.world_space_flavor == WorldSpaceFlavor.NO_FLAVOR:
            return self.short_description()
        return f"A {', '.join([flavor.name.lower() for flavor in WorldSpaceFlavor.get_flags(self.world_space_flavor)])} {self.world_space_type.name.lower()}"

    def detailed_description(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            print(self.short_description())
            print(f"Creatures: {', '.join([creature.name for creature in self.creatures])}")
            print(f"Items: {', '.join([item.name for item in self.items])}")
            print(f"Objects: {', '.join([obj.name for obj in self.world_objects])}")
            return f.getvalue()


__all__ = ["Item", "Currency", "Living", "WorldObject", "WorldSpace"]
