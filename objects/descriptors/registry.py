"""
Descriptors for registering classes, and accessing their instances.
This is useful for registering objects to systems and vice versa.
"""
import weakref


class Instances:
    """
    A class level descriptor that returns a list of all instances of the class.
        Useful for debugging, holding a registry of instances, etc.
        I chose this approach as the machinery for holding references is already
        implemented in the garbage collector, thus, we don't need to bloat memory
        with a list of weak references.
    """

    __slots__ = ()

    def __get__(self, instance, owner):
        """We grab weak references to instances of the class from the garbage collector.
            We do this because it already holds references to all objects, and we don't
        """
        return tuple(filter(lambda obj: isinstance(obj, owner), globals().setdefault('gc', __import__('gc')).get_referrers(owner)))


class RegistryMeta(type):
    """
    A metaclass that allows for mapping like use of the class.
    """

    __slots__ = ()

    def __getitem__(cls, item):
        return getattr(cls, '__registry__')[cls.cls_to_name(item)]

    def __setitem__(cls, item, value):
        getattr(cls, '__registry__')[cls.cls_to_name(item)] = value

    def __delitem__(cls, item):
        del getattr(cls, '__registry__')[cls.cls_to_name(item)]

    def __contains__(cls, item):
        return cls.cls_to_name(item) in getattr(cls, '__registry__')

    def cls_to_name(self, item):
        return item.__name__ if isinstance(item, type) else item

    def __iter__(cls):
        return iter(getattr(cls, '__registry__').items())

    def __len__(cls):
        return len(getattr(cls, '__registry__'))


class Registry(metaclass = RegistryMeta):
    """
    Registers the class with the registry. And then replaces self with an Instances descriptor.
    This means we only need to import this class to access all of the registered classes, and their instances.
    """

    __slots__ = ()
    __registry__ = weakref.WeakValueDictionary()

    def __set_name__(self, owner, name):
        """Here we register the class with the registry, and then replace self with an Instances descriptor."""
        self.__registry__.setdefault(owner.__name__, owner)
        setattr(owner, name, Instances())
        
    @classmethod
    def get(cls, name):
        """Returns the class from the registry."""
        return cls.__registry__[name]
    
    @classmethod
    def get_instances(cls, name):
        """Returns the value of the Instances descriptor from the class."""
        clz = cls.get(name)
        for k, v in clz.__dict__.items():
            if isinstance(v, Instances):
                return v.__get__(None, clz)
        raise ValueError(f"Could not find Instances descriptor for {name}")

__all__ = ['Registry', 'Instances']
