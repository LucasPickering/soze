import abc


def register(name, registry):
    def inner(cls):
        if name in registry:
            raise ValueError("Cannot register '{}' under '{}'."
                             " '{}' is already registered under that name."
                             .format(cls, name, registry[name]))
        registry[name] = cls
        return cls
    return inner


class Named(metaclass=abc.ABCMeta):

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name
