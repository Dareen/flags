from flags.models import BaseModel


class Segment(BaseModel):
    """ model for the application """

    def __init__(self, application, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def options(self):
        """ list of segment options defined for this segment """
        return self._options
