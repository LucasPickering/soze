import abc


def register(name, registry):
    def inner(cls):
        if name in registry:
            raise ValueError(
                "Cannot register '{}' under '{}'."
                " '{}' is already registered under that name.".format(
                    cls, name, registry[name]
                )
            )
        registry[name] = cls
        return cls

    return inner


class Mode(metaclass=abc.ABCMeta):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @abc.abstractclassmethod
    def _get_modes(cls):
        pass

    @classmethod
    def get_mode_names(cls):
        return set(cls._get_modes().keys())

    @classmethod
    def get_by_name(cls, name):
        return cls._get_modes()[name]
