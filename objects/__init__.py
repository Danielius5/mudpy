from .descriptors import *
from .descriptors import __all__ as _all_descriptors

class GameObject:
    registry = Registry()
    
    def __new__(cls, *args, **kwargs):
        if cls is GameObject:
            raise TypeError("Cannot instantiate Base class")
        
        for name, value in cls.__annotations__.items(): # noqa
            if issubclass(value, BaseState):
                if isinstance((var:=cls.__dict__[name]), dict):
                    state = value(**var)
                elif callable(cls.__dict__[name]):
                    state = value(default_factory = cls.__dict__[name])
                else:
                    state = value(default = cls.__dict__[name])
                state.__set_name__(cls, name)
                setattr(cls, name, state)
        
        return super().__new__(cls)
    
    
__all__ = _all_descriptors + ["GameObject"]

    
