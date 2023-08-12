import uuid
from ..descriptors import *


# noinspection PyTypeChecker
class GameObject:
    
    registry = Registry()
    uuid: int = State(default_factory = lambda: uuid.uuid4().hex, freeze = True)
    
    def __init_subclass__(cls, freeze = False, init = True,  **kwargs):
        super().__init_subclass__(**kwargs)
        for name, value in filter(lambda x: isinstance(x[1], BaseState), cls.__dict__.items()):
            if isinstance(value, BaseState):
                value.freeze = freeze
        if init:
            def __init__(self, **data):
                for k, t in self.__class__.__annotations__.items():
                    class_state = getattr(self.__class__, k, None)
                    if all([
                            isinstance(class_state, BaseState),
                            class_state.misc_data.get("required", False),
                            k not in data,
                            class_state.default is None,
                            class_state.default_factory is None,
                    ]):
                        raise TypeError(f"Missing required key: {k}")
                    if k in data:
                        setattr(self, k, data[k])

            cls.__init__ = __init__

    def __init__(self, *args, **kwargs):
        if any([
                args,
                kwargs,
        ]):
            # stub method, just to please the linter. If the init method is not overridden, it will raise an error.
            raise TypeError(f"{self.__class__.__name__}.__init__() takes exactly one argument (the instance to initialize)")
    
    def serialize(self):
        raise NotImplementedError(f"{self.__class__.__name__}.serialize() is not implemented")
    
    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError(f"{cls.__name__}.deserialize() is not implemented")

            
__all__ = ["GameObject"]