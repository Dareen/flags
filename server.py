import json
import logging

from bottle import Bottle, run, template, HTTPResponse, response
import redis

from flags.conf import settings
from flags.utils import get_key


logger = logging.getLogger(__name__)

app = Bottle()

pool = redis.ConnectionPool(connection_class=redis.Connection,
                            host=settings.REDIS_HOST,
                            port=settings.REDIS_PORT,
                            db=settings.REDIS_DB)
redis = redis.Redis(connection_pool=pool)


@app.route("/check")
def check():
    return "Up and running :)"

@app.route("/flags/<key>")
def get_flag(key):
    value = redis.get(get_key(key))
    if value:
        return {key: value}
    else:
        return HTTPResponse(body="Key does not exist!", status=404)

@app.route("/flags/")
def get_all_flags():
    response.headers["Content-Type"] = "application/json"
    keys = redis.smembers(settings.FLAGS_LIST_KEY)
    return json.dumps(list(keys))

@app.route("/flags/<key>/<value>", method="POST")
def set_flag(key, value):
    #check conflicts
    redis_key = get_key(key)
    if redis.exists(redis_key):
        return HTTPResponse(status=409, body="Key already exists! You might want to use PUT instead of POST.")

    if redis.set(redis_key, value):
        redis.sadd(settings.FLAGS_LIST_KEY, key)
        return HTTPResponse(status=201)

@app.route("/flags/<key>/<value>", method="PUT")
def set_flag(key, value):
    #check it should already exist
    redis_key = get_key(key)
    if not redis.exists(redis_key):
        return HTTPResponse(status=404, body="Key does not exists! You might want to use POST instead of PUT.")

    if redis.set(redis_key, value):
        return HTTPResponse(status=204)

@app.route("/flags/<key>", method="DELETE")
def delete_flag(key):
    if redis.delete(get_key(key)):
        redis.srem(settings.FLAGS_LIST_KEY, key)
        return HTTPResponse(status=204)
    else:
        return HTTPResponse(body="Key does not exist!", status=404)

if __name__ == "__main__":
    app_kwargs = {
        "host": settings.HOST,
        "port": settings.PORT,
        "debug": settings.DEBUG,
        "reloader": settings.DEBUG
    }

    logger.info("Starting Flags with: \n%s" % "\n".join([
        "%s: %s" % (key, value) for key, value in app_kwargs.items()
    ]))

    run(app, **app_kwargs)
