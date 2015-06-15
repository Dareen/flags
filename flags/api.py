import json
import logging
from httplib import CREATED, NOT_FOUND, NO_CONTENT, CONFLICT, UNAUTHORIZED

from bottle import HTTPResponse, response
from bottleCBV import BottleView

from flags.conf import settings
from flags.adapters.zk_adapter import ZKAdapter
from flags.errors import KeyExistsError, KeyDoesNotExistError


logger = logging.getLogger(__name__)


class FlagsView(BottleView):

    def __init__(self):
        self.adapter_type = ZKAdapter

    def index(self, application):
        response.headers["Content-Type"] = "application/json"
        with self.adapter_type() as adapter:
            return json.dumps(adapter.get_all_keys(application))

    def get(self, application, key):
        try:
            with self.adapter_type() as adapter:
                return {key: adapter.read(application, key)}
        except KeyDoesNotExistError:
            return HTTPResponse(body="Key does not exist!", status=NOT_FOUND)

    def post(self, application, key, value):
        if settings.ADMIN_MODE:
            try:
                with self.adapter_type() as adapter:
                    adapter.create(application, key, value)
                return HTTPResponse(status=CREATED)
            except KeyExistsError:
                msg = ("Key already exists! You might want to use PUT instead"
                       " of POST.")
                return HTTPResponse(status=CONFLICT, body=msg)
        else:
            return HTTPResponse(status=UNAUTHORIZED)

    def put(self, application, key, value):
        if settings.ADMIN_MODE:
            try:
                with self.adapter_type() as adapter:
                    adapter.update(application, key, value)
                return HTTPResponse(status=NO_CONTENT)
            except KeyDoesNotExistError:
                msg = ("Key does not exists! You might want to use POST "
                       "instead of PUT.")
                return HTTPResponse(status=NOT_FOUND, body=msg)
        else:
            return HTTPResponse(status=UNAUTHORIZED)

    def delete(self, application, key):
        if settings.ADMIN_MODE:
            try:
                with self.adapter_type() as adapter:
                    adapter.delete(application, key)
                return HTTPResponse(status=NO_CONTENT)
            except KeyDoesNotExistError:
                return HTTPResponse(body="Key does not exist!",
                                    status=NOT_FOUND)
        else:
            return HTTPResponse(status=UNAUTHORIZED)
