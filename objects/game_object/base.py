import contextlib
import functools
import gc
import inspect
import io
import json
import operator
import uuid
from abc import ABC
from dataclasses import dataclass, field, fields

from objects.flags import Effect, InspectionDetails, ItemSlot, ObjectAction

default_dataclass_options = dict(
        slots = True,
        repr = True,
        eq = True,
        order = False,
        frozen = False,
        unsafe_hash = False,
        init = True,
        kw_only = True,
)


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class GameObject(ABC):
    uuid: str = field(default_factory = lambda: uuid.uuid4().hex, init = False)
    allowed_actions: ObjectAction = field(default = ObjectAction.NO_ACTION,
                                          metadata = {"convert_flag_type": ObjectAction})

    def short_description(self):
        return self.__class__.__name__

    def long_description(self):
        return self.short_description()

    def detailed_description(self):
        return self.long_description()

    def action_description(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            print(self.short_description())
            print(f"Actions: {', '.join([str(action) for action in ObjectAction.get_flags(self.allowed_actions)])}")
            return f.getvalue()

    def to_dict(self, show_private = False):
        """Pulls data from the GameObject down its MRO and returns a dictionary of the data"""
        data = {}
        cls_meta = self.metadata
        for cls in filter(lambda x: all([
                issubclass(x, GameObject),
                hasattr(x, "__annotations__"),
        ]), reversed(self.__class__.__mro__)):
            for key, value in cls.__annotations__.items():
                if not cls_meta.get(key, {}).get("private", False) or show_private:
                    data[key] = getattr(self, key)
        return data

    @classmethod
    @property
    def metadata(cls):
        """Pulls metadata from fields of the GameObject down its MRO and returns a dictionary of the data"""
        return {
                field.name: field.metadata
                for field in fields(cls)
                if field.metadata
        }

    @classmethod
    def from_dict(cls, data):
        # this is for deserializing, we have to do things ever so slightly differently as 
        # some fields may not add to the init, thus we have to use setattr post init, it does mean that currently, some
        # objects will create initially default then be replaced right away, but for the very few fileds this is, I am 
        # currently fine with it
        init_keys = inspect.signature(cls.__init__).parameters.keys()
        set_attr_keys = set(init_keys) & set(data.keys())
        obj = cls(**{k: v for k, v in data.items() if k in set_attr_keys})
        for k in set_attr_keys:
            setattr(obj, k, data.get(k, getattr(obj, k, None)))
        return obj

    def to_json(self, show_private = False):
        return json.dumps(self.to_dict(
                show_private = show_private
        ), indent = 4)

    # noinspection PyTypeChecker
    @classmethod
    def from_json(cls, data):
        return json.loads(data, object_hook = cls.from_dict)

    @classmethod
    def instances(cls):
        return list(filter(lambda x: isinstance(x, cls), gc.get_objects()))

    def perform_action(self, action: ObjectAction, *args, **kwargs):

        fallback_reply = "Nothing to do here"

        if not self.allowed_actions & action:
            return fallback_reply

        match action:
            case ObjectAction.NO_ACTION:
                return fallback_reply
            case _:
                name = action.name.lower()
                method = getattr(self, name, lambda *args, **kwargs: fallback_reply)
                return method(*args, **kwargs)

    def inspect(self, lod: InspectionDetails = InspectionDetails.LONG_INSPECT):
        match lod:
            case InspectionDetails.NO_INSPECT:
                return "Nothing to see here"
            case InspectionDetails.SHORT_INSPECT:
                return self.short_description()
            case InspectionDetails.LONG_INSPECT:
                return self.long_description()
            case InspectionDetails.DETAILED_INSPECT:
                return self.detailed_description()
            case InspectionDetails.ACTION_INSPECT:
                return self.action_description()

    def __setattr__(self, key, value):
        if key in self.metadata and self.metadata[key].get("convert_flag_type", None):
            _t = self.metadata[key]["convert_flag_type"]
            value = functools.reduce(operator.or_, map(_t, _t.get_flags(value)))
        object.__setattr__(self, key, value)


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class Item(GameObject):
    name_infix: str = field(default = "")
    name_prefix: str = field(default = "")
    name_suffix: str = field(default = "")

    stack_size: int = field(default = 1)
    max_stack_size: int = field(default = 1)
    weight: float = field(default = 0.0)
    value: int = field(default = 0)

    slots: ItemSlot = field(default = ItemSlot.NO_SLOT, metadata = {"convert_flag_type": ItemSlot})
    effects: Effect = field(default = Effect.NO_EFFECT, metadata = {"convert_flag_type": Effect})

    allowed_actions: ObjectAction = field(default = ObjectAction.STACK | ObjectAction.UNSTACK | ObjectAction.INSPECT)

    compare_using_name: bool = field(default = True)

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


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class Currency(Item):
    weight: float = field(default = 0.1)
    max_stack_size: int = field(default = 100_000_000)
    value: int = field(default = 1)
    slots: ItemSlot = field(default = ItemSlot.WALLET, metadata = {"convert_flag_type": ItemSlot})
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


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
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
            metadata = {"convert_flag_type": ObjectAction}
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


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class WorldObject(GameObject):
    pass


# noinspection PyArgumentList
@dataclass(**default_dataclass_options)
class WorldSpace(GameObject):
    creatures: list[Living] = field(default_factory = list)
    items: list[Item] = field(default_factory = list)
    world_objects: list[WorldObject] = field(default_factory = list)


__all__ = [
        "GameObject",
        "Item",
        "Currency",
        "Living",
        "WorldObject",
        "WorldSpace",
]
