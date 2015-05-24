import json
import logging
from httplib import (CREATED, NOT_FOUND, NO_CONTENT, CONFLICT, UNAUTHORIZED,
                     BAD_REQUEST)

from bottle import HTTPResponse, response, request
from bottleCBV import BottleView
from schema import SchemaError

from flags.conf import settings
from flags.conf.schemas import flags_schema
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
                raise HTTPResponse(body="Key does not exist!",
                                   status=NOT_FOUND)

        def parse_segmentation(segmentation):

            # this flag is segmented
            # if any of the matching segments is different than the default
            # value, we return this segment flag
            for key in request.GET.keys():
                segment = segmentation.get(key, None)

                if segment:
                    if segment["for_all"]:
                        if segment["enabled"] != settings.DEFAULT_VALUE:
                            # this segment is enabled/disabled for all
                            return segment["enabled"]
                    else:
                        # not enabled/disabled for all, check user specific
                        # value
                        segment_options = segment.get("options", None)
                        if segment_options:
                            segmented_value = segment_options.get(
                                request.GET[key],
                                settings.DEFAULT_VALUE
                            )
                            # if it's disabled, return immediately
                            if segmented_value != settings.DEFAULT_VALUE:
                                return segmented_value

            # the flag is segmented, but the user-specific segment is not
            # specified
            return settings.DEFAULT_VALUE

        value = read_from_adapter(application, key)
        if value["for_all"]:
            # this key is disabled/enabled for all
            return {key: value["enabled"]}
        else:
            # check segmentation
            segmentation = value.get("segmentation", None)
            if not segmentation:
                return {key: value["enabled"]}

            user_flag = parse_segmentation(segmentation)
            return {key: user_flag}

    def post(self, application, key):
        if settings.ADMIN_MODE:
            try:
                flags_schema.validate(request.json)
            except SchemaError as e:
                return HTTPResponse(status=BAD_REQUEST, body=e)

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
            try:
                flags_schema.validate(request.json)
            except SchemaError as e:
                return HTTPResponse(status=BAD_REQUEST, body=e)

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
