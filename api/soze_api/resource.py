import msgpack

from .error import SozeError
from .setting import (
    Setting,
    EnumSetting,
    ColorSetting,
    FloatSetting,
    ListSetting,
    DictSetting,
)


STATUSES = ("normal", "sleep")


class Settings:
    """
    Stateless class used to convert value objects to/from Redis representation.
    This defines the structure of the data for a resource.
    """

    def __init__(self, settings):
        self._settings = settings

    def merge(self, *vals):
        def helper(settings_obj, subvals):
            if isinstance(settings_obj, Setting):
                # Get the last subval, because later values take prescedence
                return subvals[-1]

            # Recur down to each dict field and convert their values
            rv = {}
            for k, v in settings_obj.items():
                # Only recur down for values that have this field. If no values
                # have this field, then don't include it in the output at all
                next_subvals = [sv[k] for sv in subvals if k in sv]
                if next_subvals:
                    rv[k] = helper(v, next_subvals)
            return rv

        # It's easier to write logic that prioritizes the first element.
        # Reverse the input so it it prioritizes the last element from the
        # caller's perspective.
        return helper(self._settings, vals)

    def from_redis(self, val):
        def helper(settings_obj, value_obj):
            """
            Recursively converts each value in the given value dict to something
            consumable by the user, using the given settings dict.
            """
            if isinstance(settings_obj, Setting):
                return settings_obj.from_redis(value_obj)
            # settings_obj is a dict. Recur down to each dict field and
            # convert their values
            if value_obj is None:
                value_obj = {}
            return {
                k: helper(v, value_obj.get(k)) for k, v in settings_obj.items()
            }

        # Use a recursive helper to convert each nested value
        return helper(self._settings, val)

    def to_redis(self, val):
        def helper(settings_obj, value_obj):
            """
            Recursively converts each value in the given value dict to something
            consumable by Redis, using the given settings dict.
            """
            if isinstance(settings_obj, Setting):
                return settings_obj.to_redis(value_obj)
            if not isinstance(value_obj, dict):
                raise SozeError(
                    "Value must be a valid setting or a dict of settings"
                )
            # Recur down to each dict field and convert their values
            # This iterates over the value, so fields that are in the settings
            # but not in the value will be ignored.
            try:
                return {
                    k: helper(settings_obj[k], v) for k, v in value_obj.items()
                }
            except KeyError as e:
                raise SozeError(f"Unknown key: {e}")

        # Use a recursive helper to convert each nested value
        return helper(self._settings, val)


class Resource:
    def __init__(self, redis_client, name, settings):
        self._redis = redis_client
        self._name = name
        self._settings = Settings(settings)

        # The channel we publish to after changing the settings for any status
        self._pub_channel = f"a2r:{self._name}"

    @property
    def name(self):
        return self._name

    def init_redis(self):
        """
        Initializes the Redis store for this resource. For each status, this
        this will insert any missing keys into the blob, with their default
        values.
        """
        for status in STATUSES:
            self.update(status, self.get(status))

    def _get_redis_key(self, status):
        """
        Get the key that contains this resource's settings, for the given
        status. This is a msgpacked dict.
        """
        return f"user:{self._name}:{status}"

    def _redis_get(self, status):
        redis_value = self._redis.get(self._get_redis_key(status))
        return msgpack.loads(redis_value) if redis_value else {}

    def _redis_set(self, status, val):
        # Msgpack the value and push it to Redis
        self._redis.set(self._get_redis_key(status), msgpack.dumps(val))
        self._redis.publish(self._pub_channel, b"")

    def get(self, status):
        # Convert the Redis values to user-friendly values using the settings
        return self._settings.from_redis(self._redis_get(status))

    def update(self, status, value):
        # Coerce the value to something consumable by Redis. This will also
        # validate each nested value.
        converted = self._settings.to_redis(value)

        # Pull the current value, merge the converted new value into it,
        # then push that back to Redis
        current_value = self._redis_get(status)
        new_value = self._settings.merge(current_value, converted)
        self._redis_set(status, new_value)

        # Convert the merged value back to something user friendly
        return self._settings.from_redis(new_value)


class Led(Resource):
    SETTINGS = {
        "mode": EnumSetting(["off", "static", "fade"], "off"),
        "static": {"color": ColorSetting()},
        "fade": {
            "colors": ListSetting(ColorSetting()),
            "saved": DictSetting(ListSetting(ColorSetting())),
            "fade_time": FloatSetting(5.0, 1.0, 30.0),
        },
    }

    def __init__(self, redis_client):
        super().__init__(
            redis_client=redis_client, name="led", settings=__class__.SETTINGS
        )


class Lcd(Resource):
    SETTINGS = {
        "mode": EnumSetting(["off", "clock"], "off"),
        "color": ColorSetting(),
    }

    def __init__(self, redis_client):
        super().__init__(
            redis_client=redis_client, name="lcd", settings=__class__.SETTINGS
        )
