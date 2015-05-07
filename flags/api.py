import json
import logging

from bottle import HTTPResponse, response
from bottleCBV import BottleView

from flags.redis_adapter import create, read, update, delete, get_all_keys
from flags.errors import KeyExistsError, KeyDoesNotExistError


logger = logging.getLogger(__name__)


class FlagsView(BottleView):

    def index(self, application):
        response.headers["Content-Type"] = "application/json"
        return json.dumps(get_all_keys(application))

    def get(self, application, key):
        try:
            return {key: read(application, key)}
        except KeyDoesNotExistError:
            return HTTPResponse(body="Key does not exist!", status=404)

    def post(self, application, key, value):
        try:
            create(application, key, value)
            return HTTPResponse(status=201)
        except KeyExistsError:
            msg = ("Key already exists! You might want to use PUT instead of "
                   "POST.")
            return HTTPResponse(status=409, body=msg)

    def put(self, application, key, value):
        try:
            update(application, key, value)
            return HTTPResponse(status=204)
        except KeyDoesNotExistError:
            msg = ("Key does not exists! You might want to use POST instead of"
                   " PUT.")
            return HTTPResponse(status=404, body=msg)

    def delete(self, application, key):
        try:
            delete(application, key)
        except KeyDoesNotExistError:
            return HTTPResponse(body="Key does not exist!", status=404)
