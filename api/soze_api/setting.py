import abc
import pickle

from .color import BLACK, Color


class Setting(metaclass=abc.ABCMeta):
    def __init__(self, type_, default_value):
        self._type = type_
        self._default_value = default_value

    @property
    def default_value(self):
        return self._default_value

    def _validate(self, value):
        if self._type and type(value) != self._type:
            raise ValueError(
                f"Incorrect type for {value}. Expected {self._type}."
            )

    def _convert_to_redis(self, value):
        return value

    def to_redis(self, value):
        """Convert the given value to something consumable by Redis. This will
        validate the value first.

        Args:
            value (any): The value for this setting

        Returns:
            string|float|int|bytes: The value for Redis
        """
        self._validate(value)
        return self._convert_to_redis(value)

    def _convert_from_redis(self, value):
        return value

    def from_redis(self, value):
        """Convert the given value from Redis into a value for this setting.

        Args:
            value (bytes): Value from Redis

        Returns:
            any: The converted value. Type is dependent on the setting type
        """

        return (
            self._convert_from_redis(value)
            if value is not None
            else self.default_value
        )

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"<{str(self)}: default={self.default_value}>"


class EnumSetting(Setting):
    def __init__(self, valid_values, default_value):
        self._valid_values = {val.lower() for val in valid_values}
        super().__init__(None, default_value)

    def _validate(self, value):
        super()._validate(value)  # Type-checking validation
        if value.lower() not in self._valid_values:
            raise ValueError(f"Invalid value: {value}")

    def _convert_from_redis(self, value):
        return value.decode()


class ColorSetting(Setting):
    def __init__(self, default_value=BLACK.to_hexcode()):
        super().__init__(None, default_value)

    def _convert_to_redis(self, value):
        return bytes(Color.unpack(value))

    def _convert_from_redis(self, value):
        return Color.from_bytes(value).to_html()


class FloatSetting(Setting):
    def __init__(self, default_value, min_=None, max_=None):
        self._min = min_
        self._max = max_
        super().__init__(float, default_value)

    def _validate(self, value):
        # JSON has no distinction between an int and a float so we have to
        # manually cast here
        if type(value) == int:
            value = float(value)

        super()._validate(value)  # Type-checking validation

        if self._min is not None and value < self._min:
            raise ValueError(f"Value {value} below minimum of {self._min}")
        if self._max is not None and value > self._max:
            raise ValueError(f"Value {value} above maximum of {self._max}")

    def _convert_from_redis(self, value):
        return float(value)


class ListSetting(Setting):
    def __init__(self, setting, default_value=[]):
        self._setting = setting
        super().__init__(list, default_value)

    def _validate(self, value):
        super()._validate(value)
        # Validate each element
        for e in value:
            self._setting._validate(e)

    def _convert_to_redis(self, value):
        return pickle.dumps([self._setting._convert_to_redis(e) for e in value])

    def _convert_from_redis(self, value):
        return [
            self._setting._convert_from_redis(e) for e in pickle.loads(value)
        ]


class DictSetting(Setting):
    def __init__(self, setting, default_value={}):
        self._setting = setting
        super().__init__(dict, default_value)

    def _validate(self, value):
        super()._validate(value)
        # Validate each value
        for e in value.values():
            self._setting._validate(e)

    def _convert_to_redis(self, value):
        return pickle.dumps(
            {k: self._setting._convert_to_redis(v) for k, v in value.items()}
        )

    def _convert_from_redis(self, value):
        return {
            k: self._setting._convert_from_redis(v)
            for k, v in pickle.loads(value).items()
        }
