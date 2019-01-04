import flatten_dict

from .setting import (
    Setting,
    EnumSetting,
    ColorSetting,
    FloatSetting,
    ListSetting,
    DictSetting,
)


def _key_reducer(k1, k2):
    if k1:
        return f"{k1}:{k2}"
    return k2


class Resource:
    def __init__(self, redis_client, name, settings):
        self._redis = redis_client
        self._name = name
        self._settings = settings

        # The channel we publish to after changes
        self._pub_channel = f"a2r:{name}"
        # Flatten the settings dict so that each one is keyed by its
        # corresponding Redis key
        self._flat_settings = self._flatten_for_redis(settings)
        # Collect a list of all the Redis keys managed by this resource
        # Making a list is important to keep consistent iteration order
        self._redis_keys = list(self._flat_settings.keys())

    @property
    def name(self):
        return self._name

    def _flatten_for_redis(self, d):
        # Flatten the dict so it has no nested children
        flattened = flatten_dict.flatten(d, reducer=_key_reducer)
        # Add this resource's name to each key
        return {_key_reducer(self.name, k): v for k, v in flattened.items()}

    def _unflatten_from_redis(self, d):
        # Remove the key prefix from each group as you unflatten it
        return flatten_dict.unflatten(
            d, splitter=lambda key: key.split(":")[1:]
        )

    def init_redis(self):
        """
        Initializes the Redis store for this resource. This will insert any
        missing keys with their default values.
        """
        # Don't return a value from update, to prevent unnecessary Redis reads
        self.update(self.get(), return_value=False)

    def get(self):
        # Fetch all of this resource's values from redis and put them in a dict
        k_to_v = dict(zip(self._redis_keys, self._redis.mget(self._redis_keys)))

        # Convert each value using its setting. If we don't have a value for a
        # setting, then its default value will be used
        converted = {
            k: setting.from_redis(k_to_v[k])
            for k, setting in self._flat_settings.items()
        }
        return self._unflatten_from_redis(converted)

    def update(self, value, return_value=True):
        def convert(settings_obj, value_obj):
            """
            Recursively converts each value in the given value dict to something
            consumable by Redis, using the given settings dict.
            """
            if isinstance(settings_obj, Setting):
                return settings_obj.to_redis(value_obj)
            if not isinstance(value_obj, dict):
                raise ValueError("Value must be a valid setting or a dict")
            # Recur down to each dict field and convert their values
            return {
                k: convert(settings_obj[k], v) for k, v in value_obj.items()
            }

        # Coerce each value to something consumable by Redis.
        # This will also validate each value.
        converted = convert(self._settings, value)

        # Flatten the converted dict and push to Redis
        flattened = self._flatten_for_redis(converted)
        self._redis.mset(flattened)
        self._redis.publish(self._pub_channel, b"")

        # If requested, return the entire resource
        if return_value:
            return self.get()


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
