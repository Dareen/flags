import logging

import redis

from flags.conf import settings
from flags.adapters import BaseStoreAdapter
from flags.errors import KeyExistsError, KeyDoesNotExistError, RedisError


logger = logging.getLogger(__name__)


class RedisAdapter(BaseStoreAdapter):

    def __init__(self):
        pool = redis.ConnectionPool(connection_class=redis.Connection,
                                    host=settings.REDIS_HOST,
                                    port=settings.REDIS_PORT,
                                    db=settings.REDIS_DB)
        self.redis = redis.Redis(connection_pool=pool)

    @property
    def key_separator(self):
        return ":"

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_applications(self):
        raise NotImplemented

    def get_all_keys(self, application):
        keys = self.redis.smembers(self.get_key(application,
                                   settings.REDIS_ALL_FLAGS_KEY))
        return list(keys)

    def create(self, application, key, value):
        redis_key = self.get_key(application, key)

        # check conflicts
        if self.redis.exists(redis_key):
            raise KeyExistsError

        if self.redis.set(redis_key, value):
            self.redis.sadd(
                self.get_key(application, settings.REDIS_ALL_FLAGS_KEY),
                key
            )
        else:
            raise RedisError

    def read(self, application, key):
        return self.redis.get(self.get_key(application, key))

    def update(self, application, key, value):
        redis_key = self.get_key(application, key)

        # check it should already exist
        if not self.redis.exists(redis_key):
            raise KeyDoesNotExistError

        if not self.redis.set(redis_key, value):
            raise RedisError

    def delete(self, application, key):
        if self.redis.delete(self.get_key(application, key)):
            self.redis.srem(self.get_key(application), key)
        else:
            raise KeyDoesNotExistError
