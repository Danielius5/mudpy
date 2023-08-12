"""
Descriptors for referencing engine with weak references, thus not keeping them alive in memory when they are not
used any more. This is intended prevent data being kept in memory when it is not needed, and to prevent memory leaks.
This should be useful when interacting with player engine and associated engine, such as their inventory, stats etc. 
"""

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
        except AttributeError:
            return None

    def __set_name__(self, owner, name):
        self.name = name


__all__ = ["WeakProxy"]

