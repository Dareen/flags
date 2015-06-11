import logging
from abc import ABCMeta, abstractmethod, abstractproperty

from flags.conf import settings


logger = logging.getLogger(__name__)


class BaseStoreAdapter(object):

    __metaclass__ = ABCMeta

    @abstractproperty
    def key_separator(self):
        pass

    def get_key(self, *suffixes):
        return self.key_separator.join(
            map(str, filter(None,
                [settings.PREFIX, settings.VERSION] + list(suffixes)))
        )

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()
        if exc_type is not None:
            return False

        return self

    @abstractmethod
    def get_applications(self):
        pass

    @abstractmethod
    def get_all_keys(self, application):
        pass

    @abstractmethod
    def get_all_features(self, application):
        pass

    @abstractmethod
    def get_all_segments(self, application):
        pass

    @abstractmethod
    def create_feature(self, application, key, value):
        pass

    @abstractmethod
    def read_feature(self, application, key):
        pass

    @abstractmethod
    def update_feature(self, application, key, value):
        pass

    @abstractmethod
    def delete_feature(self, application, key):
        pass
