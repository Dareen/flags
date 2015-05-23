import json
import logging
from httplib import CREATED, NOT_FOUND, NO_CONTENT, CONFLICT, UNAUTHORIZED

from bottle import HTTPResponse, response, request
from bottleCBV import BottleView

from flags.conf import settings
from flags.adapters.zk_adapter import ZKAdapter
from flags.errors import KeyExistsError, KeyDoesNotExistError


logger = logging.getLogger(__name__)


class APIView(BottleView):

    def __init__(self):
        self.adapter_type = ZKAdapter

    def index(self, application):
        response.headers["Content-Type"] = "application/json"
        with self.adapter_type() as adapter:
            return json.dumps(adapter.get_all_keys(application))

    def get(self, application, key):
        def read_from_adapter(application, key):
            try:
                with self.adapter_type() as adapter:
                    return adapter.read(application, key)
            except KeyDoesNotExistError:
                return HTTPResponse(body="Key does not exist!",
                                    status=NOT_FOUND)

        def parse_segmentation(json_value):
            if isinstance(json_value, dict):
                # this flag is segmented
                # if any of the matching segments is different than the default
                # value, we return this segment flag
                for key in request.GET.keys():
                    segment = json_value.get(key, settings.DEFAULT_VALUE)

                    if segment != settings.DEFAULT_VALUE:
                        if isinstance(segment, dict):
                            segmented_value = segment.get(
                                request.GET[key],
                                settings.DEFAULT_VALUE
                            )
                            if segmented_value != settings.DEFAULT_VALUE:
                                return segmented_value
                        # only return if the segment is different than the
                        # default, otherwise keep checking other segments
                        elif segment != settings.DEFAULT_VALUE:
                            # this segment is disabled/enabled for all
                            return segment
            else:
                # this key is disabled/enabled for all
                return json_value

            # the flag is segmented, but the user-specific segment is not
            # specified
            return int(settings.DEFAULT_VALUE)

        value = read_from_adapter(application, key)
        user_flag = parse_segmentation(value)
        return {key: user_flag}

    def post(self, application, key):
        if settings.ADMIN_MODE:
            value = json.dumps(request.json)
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

    def put(self, application, key):
        if settings.ADMIN_MODE:
            value = json.dumps(request.json)
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
