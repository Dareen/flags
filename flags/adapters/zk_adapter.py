import logging
import json
import operator

from kazoo.client import KazooClient
from kazoo.exceptions import NodeExistsError, NoNodeError
from kazoo.handlers.threading import TimeoutError

from nd_service_registry import KazooServiceRegistry

from flags.conf import settings
from flags.adapters import BaseStoreAdapter
from flags.errors import (KeyExistsError,
                          KeyDoesNotExistError,
                          ZKConnectionTimeoutError)


logger = logging.getLogger(__name__)


class ZKAdapter(BaseStoreAdapter):

    # TODO: move the logic to the logical layer
    # TODO: separate the reader and the writer to different classes, since
    # they're using different clients

    # nd object handles all of the connection states
    # there is no need to start/stop or monitor the connection state at all.
    nd = KazooServiceRegistry(server=settings.ZK_HOSTS,
                              timeout=settings.ZK_CONNECTION_TIMEOUT,
                              rate_limit_calls=None)

    @property
    def key_separator(self):
        return "/"

    def get_key(self, *suffixes):
        """
        @suffixes: anything to be added after the prefix and version
        e.g. application name, key, segments ... etc.
        """
        suffixes = map(operator.methodcaller("lower"), suffixes)
        path = super(ZKAdapter, self).get_key(*suffixes)
        # append a preceeding slash in the beginning, ZK specific format
        path = "/%s" % path
        return path

    def _check_data(self, node):
        try:
            data = node["data"]
            stat = node["stat"]
        except (TypeError, KeyError) as e:
            # node is False or malformed
            # getting the node details from ZK failed.
            raise ZKConnectionTimeoutError(e)

        # if stat is None, the node does not exist
        if stat is None:
            raise KeyDoesNotExistError

        return data

    def _get_children(self, key):
        node = self.nd.get(key)
        # check if the node exists
        self._check_data(node)
        return node["children"]

    def connect(self):
        self.zk = KazooClient(hosts=settings.ZK_HOSTS)
        try:
            self.zk.start(timeout=settings.ZK_CONNECTION_TIMEOUT)
        except TimeoutError:
            raise ZKConnectionTimeoutError

    def disconnect(self):
        self.zk.stop()
        self.zk.close()

    def get_applications(self):
        try:
            # self.get_key() without params will get the root node path
            # i.e. "/flags/v1/"
            apps = self._get_children(self.get_key())
        except KeyDoesNotExistError:
            return []
        return apps

    def get_all_keys(self, *path):
        return self._get_children(self.get_key(*path))

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

    def create_feature(self, application, key, value=None):
        # Ensure a path, create if necessary
        app_path = self.get_key(application, settings.FEATURES_KEY)
        self.zk.ensure_path(app_path)

        node_path = self.get_key(application, settings.FEATURES_KEY, key)

        # default segmentation
        if value is None:
            value = self._prepare_default_feature_dict(application)

        try:
            # Create a node with data
            self.zk.create(node_path, json.dumps(value))
        except NodeExistsError:
            raise KeyExistsError

    def _prepare_default_feature_dict(self, application):
        # Create the segmentation
        segments = self._get_children(self.get_key(
            application,
            settings.SEGMENTS_KEY
        ))
        segmentation = {
            segment: {
                "toggled": settings.DEFAULT_VALUE,
                "options": {
                    option: settings.DEFAULT_VALUE
                    for option in self._get_children(
                        self.get_key(
                            application,
                            settings.SEGMENTS_KEY,
                            segment
                        )
                    )
                }
            }
            for segment in segments
        }
        return {
            "segmentation": segmentation,
            "feature_toggled": settings.DEFAULT_VALUE
        }

    def create_application(self, application):
        # ensure that /flags/v1 path exists
        root_path = self.get_key()
        self.zk.ensure_path(root_path)

        node_path = self.get_key(application)
        try:
            # Create the application node
            self.zk.create(node_path)
            # add the features and segmentation paths to the newly created app
            self.zk.ensure_path(
                self.get_key(application, settings.FEATURES_KEY)
            )
            self.zk.ensure_path(
                self.get_key(application, settings.SEGMENTS_KEY)
            )
        except NodeExistsError:
            raise KeyExistsError

    def create_segment(self, application, segment):
        # Ensure a path, create if necessary
        app_path = self.get_key(application, settings.SEGMENTS_KEY)
        self.zk.ensure_path(app_path)

        node_path = self.get_key(application, settings.SEGMENTS_KEY, segment)
        try:
            self.zk.create(node_path)
            # Update the segmentation of the existing features
            self._update_new_segment(application, segment)
        except NodeExistsError:
            raise KeyExistsError

    def _update_new_segment(self, application, segment):
        segment = segment.lower()
        features = self.get_all_keys(application, settings.FEATURES_KEY)
        for feature in features:
            feature_dict = self.read_feature(application, feature)
            feature_dict["segmentation"][segment] = {
                "toggled": settings.DEFAULT_VALUE,
                "options": dict()
            }
            self.update_feature(application, feature, feature_dict)

    def _update_new_segment_option(self, application, segment, option):
        segment = segment.lower()
        option = option.lower()
        features = self.get_all_keys(application, settings.FEATURES_KEY)
        for feature in features:
            feature_dict = self.read_feature(application, feature)
            feature_dict["segmentation"][segment]["options"][option] = settings.DEFAULT_VALUE
            self.update_feature(application, feature, feature_dict)

    def _update_deleted_segment_option(self, application, segment, option):
        segment = segment.lower()
        option = option.lower()
        features = self.get_all_keys(application, settings.FEATURES_KEY)
        for feature in features:
            feature_dict = self.read_feature(application, feature)
            del feature_dict["segmentation"][segment]["options"][option]
            self.update_feature(application, feature, feature_dict)

    def _update_deleted_segment(self, application, segment):
        segment = segment.lower()
        features = self.get_all_keys(application, settings.FEATURES_KEY)
        for feature in features:
            feature_dict = self.read_feature(application, feature)
            del feature_dict["segmentation"][segment]
            self.update_feature(application, feature, feature_dict)

    def create_segment_option(self, application, segment, option):
        # Ensure a path, create if necessary
        app_path = self.get_key(application, settings.SEGMENTS_KEY, segment)
        self.zk.ensure_path(app_path)

        node_path = self.get_key(application, settings.SEGMENTS_KEY, segment,
                                 option)
        try:
            self.zk.create(node_path)
            self._update_new_segment_option(application, segment, option)
        except NodeExistsError:
            raise KeyExistsError

    def read_feature(self, application, key):
        return self.read(application, settings.FEATURES_KEY, key)

    def read_segment(self, application, key):
        # TODO: is this needed?
        return self.read(application, settings.SEGMENTS_KEY, key)

    def read(self, *key_path):
        node = self.nd.get(path=self.get_key(*key_path))
        data = self._check_data(node)
        return data

    def update_feature(self, application, key, value):
        node_path = self.get_key(application, settings.FEATURES_KEY, key)

        try:
            self.zk.set(node_path, json.dumps(value))
        except NoNodeError:
            raise KeyDoesNotExistError

    def delete_feature(self, application, key):
        node_path = self.get_key(application, settings.FEATURES_KEY, key)

        try:
            self.zk.delete(node_path)
        except NoNodeError:
            raise KeyDoesNotExistError
