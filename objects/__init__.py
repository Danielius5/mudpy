from . import dice
from .flags import *
from .game_object import *

__all__ = game_object.__all__ + flags.__all__ + ["dice"]
