import abc
import time
import traceback
from threading import Event, Thread

from soze_reducer import logger


class RedisSubscriber(metaclass=abc.ABCMeta):
    def __init__(self, redis_client, pubsub):
        self._redis = redis_client
        self._pubsub = pubsub
        self._pubsub.subscribe(**{self.sub_channel: self._on_pub})

    @property
    @abc.abstractmethod
    def sub_channel(self):
        pass

    @abc.abstractmethod
    def _on_pub(self, msg):
        pass


class ReducerResource(RedisSubscriber):
    def __init__(self, *args, keepalive, pause=0.1, **kwargs):
        super().__init__(*args, **kwargs)
        self._keepalive = keepalive
        self._pause = pause
        self._settings = None
        self._thread = Thread(name=f"{self.name}-Thread", target=self._loop)
        self._shutdown = Event()

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    @abc.abstractmethod
    def settings_key_prefix(self):
        pass

    @property
    @abc.abstractmethod
    def pub_channel(self):
        pass

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
        # Find all keys that match out pattern
        keys = self._redis.keys(f"{self.settings_key_prefix}:*")
        # Get the values that we care about
        keys_vals = zip(keys, self._redis.mget(keys))
        self._settings = dict(keys_vals)
        self._after_reload()

    def _publish(self, msg=b""):
        self._redis.publish(self.pub_channel, msg)

    def _update(self):
        # Calculate real values if the keepalive is alive,
        # otherwise use default values
        values = (
            self._get_values()
            if self._settings and self._keepalive.is_alive
            else self._get_default_values()
        )
        # Apply the values. If something was updated, do a publish.
        if self._apply_values(*values):
            self._publish()

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

    def _after_reload(self):
        """Lifecycle method, called after API settings are reloaded from Redis.
        """
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
