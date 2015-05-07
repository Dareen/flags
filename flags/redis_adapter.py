import logging

import redis

from flags.conf import settings
from flags.errors import KeyExistsError, KeyDoesNotExistError, RedisError
from flags.utils import get_key, get_list_key


logger = logging.getLogger(__name__)


pool = redis.ConnectionPool(connection_class=redis.Connection,
                            host=settings.REDIS_HOST,
                            port=settings.REDIS_PORT,
                            db=settings.REDIS_DB)
redis = redis.Redis(connection_pool=pool)


def get_all_keys(application):
    keys = redis.smembers(get_list_key(application))
    return list(keys)


def create(application, key, value):
    redis_key = get_key(application, key)

    # check conflicts
    if redis.exists(redis_key):
        raise KeyExistsError

    if redis.set(redis_key, value):
        redis.sadd(get_list_key(application), key)
    else:
        raise RedisError


def read(application, key):
    return redis.get(get_key(application, key))


def update(application, key, value):
    redis_key = get_key(application, key)

    # check it should already exist
    if not redis.exists(redis_key):
        raise KeyDoesNotExistError

    if not redis.set(redis_key, value):
        raise RedisError


def delete(application, key):
    if redis.delete(get_key(application, key)):
        redis.srem(get_list_key(application), key)
    else:
        raise KeyDoesNotExistError
