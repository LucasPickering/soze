import abc


class Resource:
    def __init__(self, redis_client, pubsub, sub_channel):
        self._redis = redis_client
        self._pubsub = pubsub
        self._pubsub.subscribe(**{sub_channel: self._on_pub})

    @abc.abstractmethod
    def _on_pub(self, msg):
        pass

    def init(self):
        pass

    def cleanup(self):
        pass
