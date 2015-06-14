import os

from bottle import (view, TEMPLATE_PATH, request, BaseTemplate, redirect,
                    static_file)

from flags.conf import settings
from flags.adapters.zk_adapter import ZKAdapter
# from flags.errors import KeyExistsError, KeyDoesNotExistError


def register_ui_views(app):

    BaseTemplate.defaults['app'] = app  # Template global variable
    # Location of HTML templates
    TEMPLATE_PATH.insert(0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../templates'))
    )

    adapter_type = ZKAdapter

    #  Routes to static content
    @app.route('/<path:re:favicon.ico>')
    @app.route('/static/<path:path>', name='static')
    def static(path):
        'Serve static content.'
        return static_file(path, root='flags/static/')

    @app.route('/', name='applications', method=["GET", "POST"])
    @view('applications')  # Name of template
    def index():
        if request.method == "POST":
            # TODO: exception handling for ApplicationExistsError
            application_name = request.forms.new_application
            with adapter_type() as adapter:
                adapter.create_application(application_name)

        default = "Enabled" if settings.DEFAULT_VALUE else "Disabled"
        with adapter_type() as adapter:
            applications = adapter.get_applications()

        #  any local variables can be used in the template
        return locals()

    @app.route('/<application>/features', name='features', method=["GET", "POST"])
    # @app.get('/<application>', name='features')
    @view('features')  # Name of template
    def features(application):
        if request.method == "POST":
            feature_name = request.forms.new_feature
            with adapter_type() as adapter:
                adapter.create_feature(application, feature_name)

        default = "Enabled" if settings.DEFAULT_VALUE else "Disabled"
        with adapter_type() as adapter:
            flags = adapter.get_all_features(application)

        #  any local variables can be used in the template
        return locals()

    @app.route('/<application>/segments', name='segments', method=["GET", "POST"])
    @view('segments')  # Name of template
    def segments(application):
        if request.method == "POST":
            segment_name = request.forms.new_segment
            with adapter_type() as adapter:
                adapter.create_segment(application, segment_name)

        with adapter_type() as adapter:
            segments = adapter.get_all_segments(application)

        #  any local variables can be used in the template
        return locals()
