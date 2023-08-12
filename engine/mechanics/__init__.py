from . import dice

def __getattr__(name):
    for _globals in  [
            _globals for _globals in globals() if not _globals.startswith('_')
        ]:
        if hasattr(globals()[_globals], '__all__'):
            if name in globals()[_globals].__all__:
                return getattr(globals()[_globals], name)
        elif hasattr(globals()[_globals], '__getattr__'):
            try:
                return getattr(globals()[_globals], name)
            except AttributeError:
                pass
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ['dice']