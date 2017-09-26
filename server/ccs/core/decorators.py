def registered_singleton(registry, name):
    """
    Class decorator for registering a singleton class by name. When the class is registered,
    its singleton object is stored in the given registry dict, keyed by the given name.
    """
    def inner(cls):
        if name in registry:
            raise ValueError("Cannot register '{}' under '{}'."
                             " '{}' is already registered under that name."
                             .format(cls, name, registry[name]))
        registry[name] = cls()
        return cls
    return inner
