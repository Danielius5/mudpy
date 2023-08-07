from itertools import count

from .descriptors import *
from .descriptors import __all__ as _all_descriptors

import uuid

# noinspection PyTypeChecker
class GameObject:
        
    registry = Registry()
    uuid = State(default_factory = lambda: uuid.uuid4().hex, freeze = True)
    
    def __init_subclass__(cls, freeze = False, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, value in cls.__dict__.items():
            if isinstance(value, BaseState):
                value.freeze = freeze
    
__all__ = _all_descriptors + ["GameObject"]

    
