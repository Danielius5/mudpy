import gc
import weakref

class WeakProxy:
    def __set__(self, instance, value):
        if instance is None:
            return self
        instance.__dict__[self.name] = weakref.proxy(value, lambda ref: instance.__dict__.__delitem__(self.name))
        
    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.name]
        except ReferenceError:
            return None
        except KeyError:
            return None
    
    def __set_name__(self, owner, name):
        self.name = name


class WeakWrapper:
    def __init__(self, factory, *args, __default=None, **kwargs):
        self.factory = weakref.proxy(factory)
        self.args = args
        self.kwargs = kwargs
        self.default = __default


# noinspection PyArgumentList
class Factory(WeakWrapper):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return instance.__dict__.setdefault(self.name, self.factory(*self.args, **self.kwargs))
        except ReferenceError:
            return self.default

    def __set_name__(self, owner, name):
        self.name = name


# noinspection PyArgumentList
class Dynamic(WeakWrapper):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return self.factory(*self.args, **self.kwargs)
        except ReferenceError:
            return self.default


