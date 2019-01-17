import abc
import time
import traceback
from threading import Event, Thread

from soze_reducer import logger


class RedisSubscriber(metaclass=abc.ABCMeta):
    def __init__(self, redis_client, pubsub, sub_channel):
        self._redis = redis_client
        self._pubsub = pubsub
        self._pubsub.subscribe(**{sub_channel: self._on_pub})

    @abc.abstractmethod
    def _on_pub(self, msg):
        pass


class ReducerResource(RedisSubscriber):

    _MODE_KEY = "mode"

    def __init__(
        self,
        *args,
        name,
        settings_key_prefix,
        pub_channel,
        mode_class,
        pause=0.1,
        keepalive,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # Constants defined by the super class
        self._name = name
        self._settings_key_prefix = settings_key_prefix
        self._pub_channel = pub_channel
        self._mode_class = mode_class
        self._pause = pause

        # Other assorted properties
        self._keepalive = keepalive
        self._thread = Thread(name=f"{self.name}-Thread", target=self._loop)
        self._shutdown = Event()
        self._mode = None
        self._settings = None

        self._load_settings()  # Load settings from Redis for the first time

    @property
    def name(self):
        return self._name

    @property
    def thread(self):
        return self._thread

    @property
    def should_run(self):
        return not self._shutdown.is_set()

    def stop(self):
        if self.should_run:
            self._shutdown.set()

    def _on_pub(self, msg):
        self._load_settings()

    def _load_settings(self):
        # Find all keys that match our pattern
        prefix = f"{self._settings_key_prefix}:"
        keys = self._redis.keys(f"{prefix}*")

        # Get the values that we care about, and store them in a dict
        # Each key will be decoded then have its prefix removed
        self._settings = {
            k.decode()[len(prefix) :]: v
            for k, v in zip(keys, self._redis.mget(keys))
        }

        # If the mode changed, re-initialize it
        try:
            new_mode = self._settings[__class__._MODE_KEY].decode()
        except KeyError:
            pass  # No mode key in Redis, do nothing
        else:
            # Mode was available in Redis, check if it changed
            if self._mode is None or new_mode != self._mode.name:
                # Make a new mode object
                self._mode = self._mode_class.get_by_name(new_mode)()

    def publish(self, msg=b""):
        self._redis.publish(self._pub_channel, msg)

    def _update(self):
        # Calculate real values if the keepalive is alive,
        # otherwise use default values
        values = (
            self._get_values()
            if self._settings and self._keepalive.is_alive
            else self._get_default_values()
        )
        # Apply the values. If something was updated, do a publish.
        self._apply_values(*values)

    def _loop(self):
        try:
            logger.info(f"Starting {self.name} thread")
            self._after_init()
            while self.should_run:
                self._update()
                time.sleep(self._pause)
            self._before_stop()
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            logger.info(f"Stopped {self.name} thread")

    def _after_init(self):
        pass

    def _before_stop(self):
        pass

    @abc.abstractmethod
    def _get_default_values(self):
        """Get the default settings that should be used when the keepalive is
        down.
        """

        pass

    @abc.abstractmethod
    def _get_values(self):
        """Get the current values to be applied.
        """

        pass

    @abc.abstractmethod
    def _apply_values(self, *values):
        """Apply the current values to Redis. If this returns True, then a pub
        will occur after this.
        """
        pass
