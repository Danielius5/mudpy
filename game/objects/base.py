import contextlib
import functools
import gc
import inspect
import io
import json
import operator
import uuid
from dataclasses import field, fields

from ..mechanics.flags import InspectionDetails, ObjectAction
from ..system import database
from ..system.utils import go_dataclass, search_subs


# metadata explained:
# private: is not shared over the API
# to_type: is a flag type, and should be converted to the flag type when deserializing


# noinspection PyArgumentList

@go_dataclass
class BaseObject:
    category: str = field(default = "objects", init = False)

    def save(self):
        database.insert_game_object(self, cat = self.category)

    def update(self):
        database.update_game_object(self, cat = self.category)

    def delete(self):
        database.delete_game_object(self, cat = self.category)

    def is_garbage(self):
        """Override this method to determine if the object is garbage and should be collected. 
        You should include your own logic to determine if this particular
        instance is read for collection, such as being created at a certain time etc."""
        return False

    @classmethod
    def collect_garbage(cls):
        """Collects all garbage objects"""
        for obj in filter(lambda x: x.is_garbage(), cls.instances()):
            obj.delete()
            del obj

    @classmethod
    def from_db(cls, **kwargs):
        # noinspection PyArgumentList
        return database.retrieve_game_object(cls, cat = cls.category, **kwargs)

    # noinspection PyArgumentList
    @classmethod
    def from_db_all(cls, **kwargs):
        return database.retrieve_game_objects(cls, cat = cls.category, **kwargs)

    @classmethod
    def factory(cls, **kwargs):
        return ObjectFactory(cls, **kwargs)

    def to_dict(self, *keys, show_private = False):
        """Pulls data from the GameObject down its MRO and returns a dictionary of the data"""
        data = {}
        data["typename"] = self.__resolved_name__
        cls_meta = self.metadata
        for cls in filter(lambda x: all([
                issubclass(x, GameObject),
                hasattr(x, "__annotations__"),
        ]), reversed(self.__class__.__mro__)):
            for key, value in cls.__annotations__.items():
                if keys and key not in keys:
                    continue
                if not cls_meta.get(key, {}).get("private", False) or show_private:
                    data[key] = getattr(self, key)
        return data

    @classmethod
    def from_dict(cls, data: dict):
        if "typename" in data:
            del data["typename"]
        init_keys = inspect.signature(cls.__init__).parameters.keys()
        set_attr_keys = set(init_keys) & set(data.keys())
        obj = cls(**{k: v for k, v in data.items() if k in set_attr_keys})
        for k in set_attr_keys:
            setattr(obj, k, data.get(k, getattr(obj, k, None)))
        return obj

    def to_json(self, *keys, show_private = False):
        return json.dumps(self.to_dict(
                *keys,
                show_private = show_private
        ), indent = 4)

    # noinspection PyTypeChecker
    @classmethod
    def from_json(cls, data):
        return json.loads(data, object_hook = cls.from_dict)

    @classmethod
    def instances(cls):
        return list(filter(lambda x: isinstance(x, cls), gc.get_objects()))

    @classmethod
    @property
    @functools.cache
    def metadata(cls):
        """Pulls metadata from fields of the GameObject down its MRO and returns a dictionary of the data"""
        return {
                field.name: field.metadata
                for field in fields(cls)
                if field.metadata
        }

    def __getattr__(self, name):
        if name.startswith("set_"):
            return functools.partial(self.__set_field, name[4:])
        return super().__getattribute__(name)

    def __setattr__(self, key, value):
        if key in self.metadata and self.metadata[key].get("to_type", None):
            _t = self.metadata[key]["to_type"]
            if isinstance(value, str):
                value = _t[value]
            elif isinstance(value, int):
                value = functools.reduce(operator.or_, map(_t, _t.get_flags(value)))
        super().__setattr__(key, value)

    def __getstate__(self):
        return self.to_dict()

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)

    def __set_field(self, field, value):
        f"""
            Sets the field {field} to the value.
        """
        field = None
        for f in fields(self):
            if f.name == field:
                field = f
                break
        if field is None:
            raise ValueError(f"Invalid field {field}")
        setattr(self, field.name, value)

    @classmethod
    @property
    def __resolved_name__(cls):
        return ".".join(
                [_cls.__name__ for _cls in filter(lambda x: issubclass(x, GameObject), reversed(cls.__mro__))])


@go_dataclass
class GameObject(BaseObject):
    uuid: str = field(
            default_factory = lambda: uuid.uuid4().hex,
            init = False,
            repr = False
    )

    allowed_actions: ObjectAction = field(
            default = ObjectAction.NO_ACTION,
            metadata = {"to_type": ObjectAction},
            repr = False
    )

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


class ObjectFactory:
    __slots__ = ("__type", "__keys")

    def __init__(self, type_or_name = None, /, **kwargs):
        self.__type = None
        if isinstance(type_or_name, str):
            self.__type = search_subs(GameObject, type_or_name)
        elif isinstance(type_or_name, type) and issubclass(type_or_name, GameObject):
            self.__type = type_or_name
        self.__keys = kwargs

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__type.__name__ if self.__type else 'None'}, {self.__keys})"

    def create(self, **kwargs):
        return self.__type(**self.__check_args(kwargs))

    def __check_args(self, kwargs):
        if self.__type is None:
            raise ValueError("Cannot build an object factory without a type")
        kwargs.update(self.__keys)
        type_fields = fields(self.__type)
        field_names = set()
        for field in type_fields:
            field_names.add(field.name)
            if field.name not in kwargs:
                if field.default is field.default_factory is field._MISSING_TYPE:
                    raise ValueError(f"Missing required argument {field.name}")
        if not field_names.issuperset(kwargs.keys()):
            raise ValueError(f"Invalid arguments {', '.join(kwargs.keys() - field_names)}")
        return kwargs

    def bind_args(self, _kwargs = (), /, **kwargs):
        kwargs.update(self.__keys)
        kwargs.update(_kwargs)
        return self.__class__(self.__type, **kwargs)

    def unbind_args(self, *keys):
        return self.__class__(self.__type, **{k: v for k, v in self.__keys.items() if k not in keys})

    def unbind_type(self):
        return self.__class__(**self.__keys)

    def bind(self, type = None, **kwargs):
        o = self.bind_args(kwargs)
        if type is not None:
            o = o.bind_type(type)
        return o

    def unbind(self, *keys):
        return self.unbind_args(*keys).unbind_type()


__all__ = [
        "GameObject",
        "ObjectFactory"
]
