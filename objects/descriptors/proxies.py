"""Descriptors for referencing objects with weak references, thus not keeping them alive in memory when they are not
used any more. This is useful for referencing objects that are not supposed to be kept alive in memory, such as
factories, or objects that are supposed to be garbage collected when they are not used any more, such as GameObjects.
"""

import weakref


class WeakWrapper:
    def __init__(self, factory, *args, __default = None, **kwargs):
        self.factory = weakref.proxy(factory)
        self.args = args
        self.kwargs = kwargs
        self.default = __default

    def __set_name__(self, owner, name):
        self.name = name

    def replace_factory(self, factory):
        self.factory = weakref.proxy(factory)

    def replace_args(self, *args):
        self.args = args

    def replace_kwargs(self, **kwargs):
        self.kwargs = kwargs

    def replace_default(self, default):
        self.default = default

    def extend_args(self, *args):
        self.args += args

    def extend_kwargs(self, **kwargs):
        self.kwargs.update(kwargs)


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


# noinspection PyArgumentList
class Factory(WeakWrapper):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return instance.__dict__.setdefault(self.name, self.factory(*self.args, **self.kwargs))
        except ReferenceError:
            return self.default


# noinspection PyArgumentList
class Dynamic(WeakWrapper):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return self.factory(*self.args, **self.kwargs)
        except ReferenceError:
            return self.default


__all__ = ["WeakProxy", "Factory", "Dynamic"]
