import abc


class Resource:
    """
    A Resource has a Redis client and an init/cleanup procedure.
    """

    def __init__(self, redis_client):
        self._redis = redis_client

    def init(self):
        pass

    def cleanup(self):
        pass


class SubscriberResource(Resource):
    def __init__(self, *args, pubsub, sub_channel, **kwargs):
        super().__init__(*args, **kwargs)
        self._pubsub = pubsub
        self._pubsub.subscribe(**{sub_channel: self._on_pub})

    @abc.abstractmethod
    def _on_pub(self, msg):
        pass
