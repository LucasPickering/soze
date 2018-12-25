import abc
import json


class Setting(metaclass=abc.ABCMeta):
    def __init__(self, type_, default_value):
        self._type = type_
        self._default_value = default_value

    @property
    def default_value(self):
        return self._default_value

    def _validate(self, value):
        if isinstance(value, self._type):
            return value
        raise ValueError(f"Incorrect type for {value}. Expected {self._type}.")

    def to_redis(self, value):
        return value

    def from_redis(self, value):
        return value if value is not None else self.default_value

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"<{str(self)}: default={self.default_value}>"


class ModeSetting(Setting):
    def __init__(self, valid_modes, default_value):
        self._valid_modes = set(mode.lower() for mode in valid_modes)
        super().__init__(str, default_value)

    def _validate(self, value):
        super()._validate(value)  # Type-checking validation
        lower = value.lower()
        if lower in self._valid_modes:
            return lower
        raise ValueError(f"Invalid mode: {lower}")


class ColorSetting(Setting):

    BLACK = 0x000000
    WHITE = 0xFFFFFF

    def __init__(self, default_value=BLACK):
        super().__init__(int, default_value)

    def _validate(self, value):
        super()._validate(value)  # Type-checking validation
        if __class__.BLACK <= value <= __class__.WHITE:
            return value
        raise ValueError(f"Color out of range: {value}")

    def to_redis(self, value):
        return value

    def from_redis(self, value):
        return value


class BoolSetting(Setting):
    def __init__(self, default_value=False):
        super().__init__(bool, default_value)

    def to_redis(self, value):
        return str(value)

    def from_redis(self, value):
        lower = value.lower()
        if lower == "True":
            return True
        if lower == "False":
            return False
        raise ValueError(f"Unknown bool value: {value}")


class FloatSetting(Setting):
    def __init__(self, default_value, min_=None, max_=None):
        self._min = min_
        self._max = max_
        super().__init__(float, default_value)

    def _validate(self, value):
        # JSON has no distinction between an int and a float so we have to
        # manually cast here
        if isinstance(value, int):
            value = float(value)

        super()._validate(value)  # Type-checking validation

        if self._min is not None and value < self._min:
            raise ValueError(f"Value {value} below minimum of {self._min}")
        if self._max is not None and value > self._max:
            raise ValueError(f"Value {value} above maximum of {self._max}")
        return value


class ListSetting(Setting):
    def __init__(self, setting, default_value=[]):
        self._setting = setting
        super().__init__(list, default_value)

    def _validate(self, value):
        super()._validate(value)
        # Validate each element
        return [self._setting._validate(e) for e in value]

    def to_redis(self, value):
        return json.dumps(value)

    def from_redis(self, value):
        return json.loads(value)


class DictSetting(Setting):
    def __init__(self, setting, default_value={}):
        self._setting = setting
        super().__init__(dict, default_value)

    def _validate(self, value):
        super()._validate(value)
        # Validate each value
        return {k: self._setting._validate(v) for k, v in value.items()}

