import redis

from . import logger, util
from .setting import (
    ModeSetting,
    ColorSetting,
    BoolSetting,
    FloatSetting,
    ListSetting,
    DictSetting,
)


class Settings:
    """
    @brief      The settings directly determined by the user. These are all set
                from the API.
    """

    SETTINGS = {
        "led": {
            "mode": ModeSetting(["off", "static", "fade"], "off"),
            "static": {"color": ColorSetting()},
            "fade": {
                "colors": ListSetting(ColorSetting()),
                "saved": DictSetting(ListSetting(ColorSetting())),
                "fade_time": FloatSetting(5.0, 1.0, 30.0),
            },
        },
        "lcd": {
            "mode": ModeSetting(["off", "clock"], "off"),
            "color": ColorSetting(),
            "link_to_led": BoolSetting(),
        },
    }

    def __init__(self, redis_url):
        # This doesn't actually initialize a connection
        self._redis = redis.from_url(redis_url)

    def init_redis(self):
        # Settings could have changed during load, e.g. new settings that
        # weren't in Redis. Save again to get those into Redis.
        logger.info("Initializing Redis data...")
        self.set("", self.get(""))
        logger.info("Redis initialized")

    def get(self, path):
        key_prefix = util.to_colon_path(path)
        # Get a dict of all settings we want to fetch, keyed by their Redis key
        settings = util.to_redis(
            util.get_at_path(__class__.SETTINGS, key_prefix), key_prefix
        )

        # Put the keys into a list for consistent iteration order,
        # then fetch their corresponding values and store them in a dict
        keys_list = list(settings.keys())
        k_to_v = dict(zip(keys_list, self._redis.mget(keys_list)))

        # Convert each value using its setting. If we don't have a value for a
        # setting, then its default value will be used
        converted = {
            k: setting.from_redis(k_to_v[k]) for k, setting in settings.items()
        }

        # Unflatten the list of values into a dict and return it
        return util.from_redis(converted, key_prefix)

    def set(self, path, value):
        key_prefix = util.to_colon_path(path)
        settings = util.to_redis(
            util.get_at_path(__class__.SETTINGS, key_prefix), key_prefix
        )
        subvals = util.to_redis(value, key_prefix)
        coerced = {k: settings[k].to_redis(v) for k, v in subvals.items()}

        # Push to Redis and do debug logging
        self._redis.mset(coerced)
        for k, v in coerced.items():
            logger.debug(f"Set {k} to {v}")

        return util.from_redis(coerced, key_prefix)
