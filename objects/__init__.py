from .descriptors import *
from .descriptors import __all__ as _all_descriptors

import uuid
import typing

# noinspection PyTypeChecker
class GameObject:
        
    registry = Registry()
    uuid: int = State(default_factory = lambda: uuid.uuid4().hex, freeze = True)    
    
    def __init_subclass__(cls, freeze = False, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, value in filter(lambda x: isinstance(x[1], BaseState), cls.__dict__.items()):
            if isinstance(value, BaseState):
                value.freeze = freeze 

    def __init__(self, *args, **kwargs):
        kwargs.update(dict(zip(self.__class__.__annotations__, args)))
        keys = set(kwargs.keys())
        required_keys = set()
        for k, t in self.__class__.__annotations__.items():
            if not any([
                    hasattr(self, k),
                    isinstance(t, typing._UnionGenericAlias) and any(isinstance(arg, typing._SpecialForm) and arg._name in ["Any", "NoneType"] for arg in t.__args__),
                    isinstance(t, typing._SpecialForm) and t._name == "NoneType",
                    isinstance(getattr(self.__class__, k), BaseState) and (getattr(self.__class__, k).default is not None or getattr(self.__class__, k).default_factory is not None),
            ]):
                required_keys.add(k)
        if not keys.issuperset(required_keys):
            raise TypeError(f"Missing required keys: {required_keys - keys}")
        for k, v in kwargs.items():
            if k not in self.__class__.__annotations__:
                raise TypeError(f"Invalid key: {k}")
            setattr(self, k, v)
        
                
__all__ = _all_descriptors + ["GameObject"]

    
