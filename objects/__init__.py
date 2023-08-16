from objects.game_object.flags import *
from .game_object import *
from .game_object import dice

__all__ = game_object.__all__ + flags.__all__ + ["dice"]
