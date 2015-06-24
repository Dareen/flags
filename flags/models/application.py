import logging

from flags.models import BaseModel
# from flags.models.segment import Segment

logger = logging.getLogger(__name__)


class Application(BaseModel):
    """ model for the application. """

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        """ the name of the application. """
        return self._name

    @property
    def segments(self):
        """ list of segments defined for this application. """
        return self._segments

    @property
    def features(self):
        """ list of features configured for this application. """
        return self._features

    @property
    def parsed_features(self):
        return self._parsed_features
