from descriptors.state import State
from descriptors.registry import Registry

from uuid import uuid4

class GameObject:
    registry = Registry()
    
    def __new__(cls, *args, **kwargs):
        if cls is GameObject:
            raise TypeError("Cannot instantiate Base class")
        
        for name, value in cls.__annotations__.items(): # noqa
            if issubclass(value, State) and isinstance(cls.__dict__[name], dict):
                state = value(**cls.__dict__[name])
                state.__set_name__(cls, name)
                setattr(cls, name, state)
        
        return super().__new__(cls)
    
    
if __name__ == "__main__":
    class User(GameObject):
        uuid: State[str] = {"default_factory": lambda: f"User-{uuid4().hex}"}
        name: State[str] = {"default": "Anonymous"}
        active: State[bool] = {"default": False}
    
    u = User()
    print(u.uuid)
    print(u.name)
    print(u.active)
    print(User.registry)
    
