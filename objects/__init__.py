from objects.flags import *
from . import dice
from .game_object import *

__all__ = game_object.__all__ + flags.__all__ + ["dice"]
