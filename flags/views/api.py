import logging
from httplib import NOT_FOUND, BAD_REQUEST

from bottle import HTTPResponse, response, request
from bottleCBV import BottleView

from flags.conf import settings
from flags.adapters.zk_adapter import ZKAdapter
from flags.errors import KeyDoesNotExistError


logger = logging.getLogger(__name__)


class APIView(BottleView):

    # /api/<application>/basic/
    # /api/<application>/basic/<feature>
    # /api/<application>/advanced/
    # /api/<application>/advanced/<feature>

    def __init__(self):
        self.adapter_type = ZKAdapter

    # TODO: use regex for mode
    def index(self, application, mode=settings.RESPONSE_MODE_BASIC):
        response.headers["Content-Type"] = "application/json"
        try:
            with self.adapter_type() as adapter:
                application_features = adapter.get_all_keys(
                    application, settings.FEATURES_KEY
                )
        except KeyDoesNotExistError:
            msg = ("Application %s does not exists!" % application)
            return HTTPResponse(status=NOT_FOUND, body=msg)

        if mode == settings.RESPONSE_MODE_BASIC:
            # sample response:
            # {"feature1": false, "feature2": true}
            user_features = dict()
            for feature in application_features:
                user_features[feature] = self._parse_feature(application,
                                                             feature)
            return user_features

        elif mode == settings.RESPONSE_MODE_ADVANCED:
            # sample response:
            # {
            #     "feature1": {
            #         "user_enabled": true,
            #         "feature_toggled": true,
            #         "segmentation":{
            #             "platform": {
            #                 "toggled": true,
            #                 "options": {
            #                     "iOS": true,
            #                     "Android": false
            #                 }
            #             },
            #             "country": {
            #                 "toggled": true,
            #                 "options": {
            #                     "7": true,
            #                     "4": false
            #                 }
            #             }
            #         }
            #     },
            #     "feature2": {
            #         "user_enabled": true,
            #         "feature_toggled": true,
            #         "segmentation":{
            #             "platform": {
            #                 "toggled": true,
            #                 "options": {
            #                     "iOS": true,
            #                     "Android": false
            #                 }
            #             },
            #             "country": {
            #                 "toggled": true,
            #                 "options": {
            #                     "7": true,
            #                     "4": false
            #                 }
            #             }
            #         }
            #     }
            # }
            feature_dicts = dict()
            for feature in application_features:
                feature_dicts[feature] = self.read_feature(application,
                                                           feature)
                feature_dicts[feature]["user_enabled"] = self._parse_feature(
                                                             application,
                                                             feature)
            return feature_dicts
        else:
            msg = ("Invalid mode %s, please select either %s or %s." %
                   (mode, settings.RESPONSE_MODE_BASIC,
                    settings.RESPONSE_MODE_ADVANCED))
            return HTTPResponse(status=BAD_REQUEST, body=msg)

    def get(self, application, mode, feature):
        if mode == settings.RESPONSE_MODE_BASIC:
            return {feature: self._parse_feature(application, feature)}
        elif mode == settings.RESPONSE_MODE_ADVANCED:
            feature_dict = self.read_feature(application, feature)
            feature_dict["user_enabled"] = self._parse_feature(application,
                                                               feature)
            return feature_dict
        else:
            msg = ("Invalid mode %s, please select either %s or %s." %
                   (mode, settings.RESPONSE_MODE_BASIC,
                    settings.RESPONSE_MODE_ADVANCED))
            return HTTPResponse(status=BAD_REQUEST, body=msg)

    def read_feature(self, application, feature):
        try:
            with self.adapter_type() as adapter:
                return adapter.read_feature(application, feature)
        except KeyDoesNotExistError:
            raise HTTPResponse(body="Feature %s does not exist!" % feature,
                               status=NOT_FOUND)

    def _parse_feature(self, application, feature):
        """ read an application key/feature and parse the result based on the
        user segmentation passed in the request GET params
        """

        def parse_segmentation(segmentation):

            # TODO: this can be refactored to be dynamic

            # this flag is segmented
            # if any of the matching segments is different than the default
            # value, we return this segment flag
            for feature in request.GET.keys():
                segment = segmentation.get(feature.lower(), None)

                if segment:
                    if segment["toggled"] != settings.DEFAULT_VALUE:
                        # this segment is enabled/disabled for all
                        return segment["toggled"]
                    else:
                        # not enabled/disabled for all, check user specific
                        # value
                        segment_options = segment["options"]
                        segmented_value = segment_options.get(
                            request.GET[feature].lower(),
                            settings.DEFAULT_VALUE
                        )
                        # if it's disabled, return immediately, no need to
                        # parse the rest of the segments, one disabled segment
                        # is enough to disable it fot that user
                        if segmented_value != settings.DEFAULT_VALUE:
                            return segmented_value

            # the user-specific segment is not available in this application
            return settings.DEFAULT_VALUE

        feature_dict = self.read_feature(application, feature)
        # If DEFAULT_VALUE is True, then features are Enabled unless stated
        # otherwise
        # If DEFAULT_VALUE is False, then features are Disabled unless stated
        # otherwise
        if feature_dict["feature_toggled"] != settings.DEFAULT_VALUE:
            # the feature itself is disabled (if DEFAULT_VALUE is True) so no
            # need to look at the segmentation
            return feature_dict["feature_toggled"]
        else:
            # check segmentation
            segmentation = feature_dict["segmentation"]
            return parse_segmentation(segmentation)
