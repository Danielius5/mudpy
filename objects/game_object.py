import contextlib
import inspect
import io
import json
import uuid
from abc import ABC
from dataclasses import dataclass, field

from objects.flags import CanInspect, DamageType, Effect, ItemSlot, ObjectAction


@dataclass
class GameObject(ABC):
    uuid: str = field(default_factory = lambda: uuid.uuid4().hex, init = False)
    actions: ObjectAction = ObjectAction.NO_ACTION

    def short_description(self):
        return self.__class__.__name__

    def long_description(self):
        return self.short_description()

    def detailed_description(self):
        return self.long_description()

    def action_description(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            print(self.short_description())
            print(f"Actions: {', '.join([str(action) for action in ObjectAction.get_flags(self.actions)])}")
            return f.getvalue()

    def to_dict(self):
        data = {}
        for cls in filter(lambda x: all([
                issubclass(x, GameObject),
                hasattr(x, "__annotations__"),
        ]), reversed(self.__class__.__mro__)):
            for key, value in cls.__annotations__.items():
                data[key] = getattr(self, key)
        return data

    @classmethod
    def from_dict(cls, data):
        init_keys = inspect.signature(cls.__init__).parameters.keys()
        set_attr_keys = set(init_keys) & set(data.keys())
        obj = cls(**{k: v for k, v in data.items() if k in set_attr_keys})
        for k in set_attr_keys:
            setattr(obj, k, data.get(k, getattr(obj, k, None)))
        return obj

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, data):
        return json.loads(data, object_hook = cls.from_dict)

    def perform_action(self, action: ObjectAction, *args, **kwargs):
    
        fallback_reply = "Nothing to do here"
        
        if not self.actions & action:
            return fallback_reply

        match action:
            case ObjectAction.NO_ACTION:
                return fallback_reply
            case _:
                name = action.name.lower()
                method = getattr(self, name, lambda *args, **kwargs: fallback_reply)
                return method(*args, **kwargs)
            
    def inspect(self, lod: CanInspect):
        match lod:
            case CanInspect.NO_INSPECT:
                return "Nothing to see here"
            case CanInspect.SHORT_INSPECT:
                return self.short_description()
            case CanInspect.LONG_INSPECT:
                return self.long_description()
            case CanInspect.DETAILED_INSPECT:
                return self.detailed_description()
            case CanInspect.ACTION_INSPECT:
                return self.action_description()


@dataclass
class Item(GameObject):
    name_infix: str = ""
    name_prefix: str = ""
    name_suffix: str = ""

    slot: ItemSlot = ItemSlot.NO_SLOT
    effects: Effect = Effect.NO_EFFECT

    stack_size: int = 1
    max_stack_size: int = 1
    weight: float = 0.0
    value: int = 0

    actions: ObjectAction = ObjectAction.STACK | ObjectAction.UNSTACK | ObjectAction.INSPECT

    def short_description(self):
        return self.name_infix

    def long_description(self):
        return f"{self.name_prefix} {self.name_infix} {self.name_suffix}".strip()

    def detailed_description(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            print(f"Name: {' '.join([part for part in [self.name_prefix, self.name_infix, self.name_suffix] if part])}")
            if self.slot != ItemSlot.NO_SLOT:
                print(f"Slot: {self.slot}")
            if self.effects != Effect.NO_EFFECT:
                print(f"Effects: {', '.join([str(effect) for effect in Effect.get_flags(self.effects)])}")
            print(f"Stack Size: {self.stack_size}")
            print(f"Weight: {self.stack_weight}")
            print(f"Value: {self.stack_value}")
            return f.getvalue()

    @property
    def stack_weight(self):
        return self.weight * self.stack_size
    
    @property
    def stack_value(self):
        return self.value * self.stack_size

    def stack(self, other):
        if not self.actions & ObjectAction.STACK:
            return "Nothing to stack here"
        if not isinstance(other, self.__class__):
            raise ValueError("Cannot stack two different items")
        if self.name_infix != other.name_infix:
            raise ValueError("Cannot stack two different items")
        if self.stack_size + other.stack_size > self.max_stack_size:
            raise ValueError("Cannot stack two items over the max stack size")
        self.stack_size += other.stack_size
        del other
        return self
    

@dataclass
class Currency(Item):
    weight: float = 0.1
    max_stack_size: int = 100_000_000
    value: int = 1
    slot: ItemSlot = ItemSlot.WALLET

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

    def stack(self, other):
        if not isinstance(other, Currency):
            raise ValueError("Cannot stack two different items")
        if self.stack_size + other.stack_size > self.max_stack_size:
            raise ValueError("Cannot stack two items over the max stack size")
        self.stack_size += other.stack_size
        del other
        return self


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
    
@dataclass
class Consumable(Item):
    ...


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
    pass


@dataclass
class WeaponMod(Item):
    pass


if __name__ == "__main__":
    currency = Currency()
    currency.stack_size = 1000
    print(currency.perform_action(ObjectAction.DROP))
