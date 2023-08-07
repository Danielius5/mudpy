from .registry import __all__ as _registry_all
from .registry import *
from .state import __all__ as _state_all
from .state import *
from .proxies import __all__ as _proxies_all
from .proxies import *

__all__ = _registry_all + _state_all + _proxies_all

def __getattr__(name):
    if name in __all__:
        return __import__(name)
    raise AttributeError(f"module {__name__} has no attribute {name}")