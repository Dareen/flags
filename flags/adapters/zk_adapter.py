import logging
import json

from kazoo.client import KazooClient
from kazoo.exceptions import NodeExistsError, NoNodeError

from flags.conf import settings
from flags.adapters import BaseStoreAdapter
from flags.errors import KeyExistsError, KeyDoesNotExistError


logger = logging.getLogger(__name__)


class ZKAdapter(BaseStoreAdapter):

    @property
    def key_separator(self):
        return "/"

    def get_key(self, *suffixes):
        # *suffixes: anything to be added after the prefix and version
        # e.g. application name, key, segments ... etc.
        path = super(ZKAdapter, self).get_key(*suffixes)
        # append a preceeding slash in the beginning, ZK specific format
        path = "/%s" % path
        return path

    def connect(self):
        self.zk = KazooClient(hosts=settings.ZK_HOSTS)
        self.zk.start(timeout=settings.ZK_CONNECTION_TIMEOUT)

    def disconnect(self):
        self.zk.stop()

    def get_applications(self):
        try:
            # self.get_key() without params will get the root node path
            # i.e. "/flags/v1/"
            apps = self.zk.get_children(self.get_key())
        except NoNodeError:
            return []
        return apps

    def get_all_keys(self, *path):
        try:
            keys = self.zk.get_children(self.get_key(*path))
        except NoNodeError:
            return []
        return keys

    def get_all_features(self, application):
        keys = self.get_all_keys(application, settings.FEATURES_KEY)
        items = dict()
        for key in keys:
            items[key] = self.read_feature(application, key)
        return items

    def get_all_segments(self, application):
        segments = self.get_all_keys(application, settings.SEGMENTS_KEY)
        items = dict()
        for segment in segments:
            # Read the options in each segment
            items[segment] = self.get_all_keys(
                application,
                settings.SEGMENTS_KEY,
                segment
            )
        return items

    def create_feature(self, application, key, value):
        # Ensure a path, create if necessary
        app_path = self.get_key(application, settings.FEATURES_KEY)
        self.zk.ensure_path(app_path)

        node_path = self.get_key(application, settings.FEATURES_KEY, key)
        try:
            # Create a node with data
            self.zk.create(node_path, value)
        except NodeExistsError:
            raise KeyExistsError

    def read_feature(self, application, key):
        return self.read(application, settings.FEATURES_KEY, key)

    def read_segment(self, application, key):
        return self.read(application, settings.SEGMENTS_KEY, key)

    def read(self, *key_path):
        try:
            # zk.retry will automatically retry upon zk connection failure
            data, stat = self.zk.retry(
                self.zk.get,
                self.get_key(*key_path)
            )
            try:
                return json.loads(data)
            except ValueError:
                return data

        except NoNodeError:
            raise KeyDoesNotExistError

    def update_feature(self, application, key, value):
        node_path = self.get_key(application, settings.FEATURES_KEY, key)

        try:
            self.zk.set(node_path, value)
        except NoNodeError:
            raise KeyDoesNotExistError

    def delete_feature(self, application, key):
        node_path = self.get_key(application, settings.FEATURES_KEY, key)

        try:
            self.zk.delete(node_path)
        except NoNodeError:
            raise KeyDoesNotExistError
