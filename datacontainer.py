from typing import Generic, TypeVar

T = TypeVar('T')

class State(Generic[T]):
    def __init__(self, default=None, _type=None):
        self.default = default
        self.type = _type or type(default) if default is not None else None
        
    def __set_name__(self, owner, name):
        self.name = name
        
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name, self.default)
    
    def __set__(self, instance, value):
        if self.type is not None:
            if not isinstance(value, self.type):
                raise TypeError(f"Expected {self.type}, got {type(value)}")
        instance.__dict__[self.name] = value
        
    def __delete__(self, instance):
        del instance.__dict__[self.name]
        