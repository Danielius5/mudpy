import abc
import functools
import inspect
import json
import operator
import typing
import uuid
from dataclasses import fields

from game.mechanics.flags import GameFlags
from game.system.utils import go_dataclass as ddc, private_hidden_field as phf, search_subs


def search_subs_from_resolved_name(cls, name):
    # if cls.__resolved_name__ == name:
    #     return cls
    # for sub in cls.__subclasses__():
    #     if (result := search_subs_from_resolved_name(sub, name)):
    #         return result
    # we split the name by ., and working left to right find the next subclass until we reach the end
    # if we reach the end, we return the last subclass, if we don't we return None
    sub = None
    for n in name.split("."):
        sub = search_subs(sub or cls, n)
        if sub is None:
            break
    return sub


@ddc
class BaseObject:
    uuid: str = phf(default_factory = lambda: uuid.uuid4().hex)

    @classmethod
    @functools.cache
    def factory(cls) -> "ObjectFactory":
        return ObjectFactory(cls)

    @classmethod
    @property
    @functools.cache
    def metadata(cls):
        """Pulls metadata from fields of the BaseObject down its MRO and returns a dictionary of the data"""
        return {
                field.name: field.metadata
                for field in fields(cls)
                if field.metadata
        }

    def __getattr__(self, name):
        if name.startswith("set_"):
            return functools.partial(self.__set_field, name[4:])
        return object.__getattribute__(self, name)

    def __setattr__(self, key, value):
        if key in self.metadata:
            meta = self.metadata[key]
            if meta.get("to_type", None):
                _t = self.metadata[key]["to_type"]
                try:
                    if issubclass(_t, GameFlags):
                        if isinstance(value, str):
                            value = _t[value]
                        elif isinstance(value, int):
                            value = functools.reduce(operator.or_, map(_t, _t.get_flags(value)))
                    elif issubclass(_t, BaseObject):
                        if not isinstance(value, BaseObject):
                            if isinstance(value, dict):
                                value = _t.from_dict(value)
                            elif isinstance(value, tuple):
                                value = _t.from_dict(dict.fromkeys(value))
                            elif isinstance(value, str):
                                value = _t.from_db(uuid = value)
                except TypeError:
                    pass
                else:
                    if callable(_t):
                        value = _t(value)
            elif meta.get("post_process", None):
                _t = self.metadata[key]["post_process"]
                if not callable(_t):
                    raise ValueError(f"Invalid post process type {_t}")
                value = _t(value)
        object.__setattr__(self, key, value)

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
                [
                        _cls.__name__
                        for _cls
                        in filter(
                        lambda x: issubclass(x, BaseObject),
                        reversed(cls.__mro__)
                )])

    @classmethod
    def from_dict(cls, data: dict):
        t = cls
        if "resolved_name" in data:
            t = search_subs_from_resolved_name(BaseObject, data["resolved_name"])
        init_keys = inspect.signature(cls.__init__).parameters.keys()
        set_attr_keys = set(init_keys) & set(data.keys())
        obj = t(**{k: v for k, v in data.items() if k in set_attr_keys})
        for k in set_attr_keys:
            setattr(obj, k, data.get(k, getattr(obj, k, None)))
        return obj

    @classmethod
    def from_json(cls, data):
        return json.loads(data, object_hook = cls.from_dict)

    def to_dict(self, *keys, show_private = False):
        """Pulls data from the BaseObject down its MRO and returns a dictionary of the data"""
        data = {}
        data["resolved_name"] = self.__resolved_name__
        cls_meta = self.metadata
        for field in fields(self):
            if keys and field.name not in keys:
                continue
            if not cls_meta.get(field.name, {}).get("private", False) or show_private:
                v = getattr(self, field.name)
                if isinstance(v, BaseObject):
                    v = v.to_dict()
                elif isinstance(v, type) and issubclass(type(v), BaseObject):
                    v = v.__name__.split(".")[-1]
                data[field.name] = v
        return data

    def to_json(self, *keys, show_private = False):
        return json.dumps(self.to_dict(
                *keys,
                show_private = show_private
        ), indent = 4)


T = typing.TypeVar("T", bound = BaseObject, covariant = True)


class ObjectFactory(typing.Generic[T]):
    __slots__ = ("__type", "__keys", "__field_names")

    def __init__(
            self,
            type_or_name: typing.Type[T] = None,
            /,
            **kwargs
    ):
        self.__type = None
        if isinstance(type_or_name, str):
            self.__type = search_subs_from_resolved_name(BaseObject, type_or_name)
        elif isinstance(type_or_name, type) and issubclass(type_or_name, BaseObject):
            self.__type = type_or_name
        if self.__type is not None:
            self.__field_names = set([field.name for field in fields(self.__type)])
        self.__keys = kwargs

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__type.__name__ if self.__type else 'None'}, {self.__keys})"

    def create(self, **kwargs) -> T:
        return self.__type.from_dict(self.__process_args(kwargs))

    def __check_args(self, kwargs):
        if self.__type is None:
            raise ValueError("Cannot build an object factory without a type")
        if not issubclass(self.__type, BaseObject):
            raise ValueError("Cannot build an object factory without a BaseObject type")
        kwargs.update(self.__keys)
        type_fields = fields(self.__type)
        if not self.__field_names.issuperset(kwargs.keys()):
            raise ValueError(f"Invalid arguments {', '.join(kwargs.keys() - self.field_names)}")
        for field in type_fields:
            if field.name not in kwargs:
                if field.default is field.default_factory is field._MISSING_TYPE:
                    raise ValueError(f"Missing required argument {field.name}")
        return kwargs

    def __build_args(self, kwargs):
        for key, value in kwargs.items():
            if isinstance(value, ObjectFactory):
                kwargs[key] = value.create()
        return kwargs

    def __process_args(self, kwargs):
        return self.__build_args(self.__check_args(kwargs))

    def bind_type(
            self, __type: typing.Type[T] = None, /
    ):
        return self.__class__(__type, **self.__keys)

    def bind_args(self, _kwargs = (), /, **kwargs):
        kwargs.update(self.__keys)
        kwargs.update(_kwargs)
        return self.__class__(self.__type, **kwargs)

    def bind(
            self,
            __type: typing.Type[T] = None,
            /,
            **kwargs
    ):
        o = self.bind_args(kwargs)
        if __type is not None:
            o = o.bind_type(__type)
        return o

    def get_bound_type(self):
        return self.__type

    def get_bound_args(self):
        return self.__keys


class BaseObjectMixin(abc.ABC):
    def __new__(cls, *args, **kwargs):
        if cls is BaseObjectMixin:
            raise TypeError("BaseObjectMixin cannot be instantiated")
        elif not issubclass(cls, BaseObject):
            raise TypeError(f"{cls.__name__} must be a subclass of BaseObject")
        return super().__new__(cls)


__all__ = [
        "BaseObject",
        "ObjectFactory",
]
