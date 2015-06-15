import os

from bottle import (view, TEMPLATE_PATH, request, BaseTemplate, redirect,
                    static_file, abort)

from flags.conf import settings
from flags.adapters.zk_adapter import ZKAdapter
from flags.errors import KeyExistsError, KeyDoesNotExistError


def register_ui_views(app):

    BaseTemplate.defaults['app'] = app  # Template global variable
    # Location of HTML templates
    TEMPLATE_PATH.insert(0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../templates'))
    )

    # TODO: API and UI must use the same adapter
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
            if application_name:
                with adapter_type() as adapter:
                    adapter.create_application(application_name)
            else:
                # TODO: format errors in a nice UI
                abort(400, "Please provide a name for the new application.")

        default = "Enabled" if settings.DEFAULT_VALUE else "Disabled"
        with adapter_type() as adapter:
            applications = adapter.get_applications()

        #  any local variables can be used in the template
        return locals()

    @app.route('/<application>/features', name='features',
               method=["GET", "POST"])
    @view('features')  # Name of template
    def features(application):
        application = application.title()

        if request.method == "POST":
            feature_chck_name_tmpl = "%s_checkbox"
            segment_chck_name_tmpl = "%s_%s_checkbox"
            option_chck_name_tmpl = "%s_%s_%s_checkbox"

            with adapter_type() as adapter:
                segments = adapter.get_all_segments(application)
                features = adapter.get_all_features(application)

                for feature in features:
                    # a checkbox is checked if it exists in request.forms
                    feature_dict = {
                        "enabled": True if request.forms.get(
                            feature_chck_name_tmpl % feature
                        ) else False,
                        "segmentation": {
                            segment: {
                                "enabled": True if request.forms.get(
                                    segment_chck_name_tmpl % (feature, segment)
                                ) else False,
                                "options": {
                                    option: True if request.forms.get(
                                        option_chck_name_tmpl %
                                        (feature, segment, option)
                                    ) else False
                                    for option in segments[segment]
                                }
                            }
                            for segment in segments
                        }
                    }
                    adapter.update_feature(application, feature, feature_dict)

        default = "Enabled" if settings.DEFAULT_VALUE else "Disabled"
        try:
            with adapter_type() as adapter:
                features = adapter.get_all_features(application)
        except KeyDoesNotExistError:
            abort(404, "Application %s does not exist." % application)


        #  any local variables can be used in the template
        return locals()

    # TODO: change this crappy URL later
    @app.post('/<application>/create', name='create')
    def create_feature(application):
        feature_name = request.forms.new_feature
        if feature_name:
            # TODO: exception handling
            with adapter_type() as adapter:
                adapter.create_feature(application, feature_name)
        else:
            # TODO: format errors in a nice UI
            abort(400, "Please provide a name for the new feature.")

        redirect(app.get_url('features', application=application))

    @app.route('/<application>/segments', name='segments',
               method=["GET", "POST"])
    @view('segments')  # Name of template
    def segments(application):
        application = application.title()
        if request.method == "POST":
            segment_name = request.forms.new_segment
            if segment_name:
                # TODO: exception handling
                with adapter_type() as adapter:
                    adapter.create_segment(application, segment_name)
            else:
                # TODO: format errors in a nice UI
                abort(400, "Please provide a name for the new segment.")

        try:
            with adapter_type() as adapter:
                features = adapter.get_all_segments(application)
        except KeyDoesNotExistError:
            abort(404, "Application %s does not exist." % application)

        #  any local variables can be used in the template
        return locals()

    @app.post('/<application>/options/<segment>', name='options')
    def options(application, segment):
        option_name = request.forms.new_option
        if option_name:
            # TODO: exception handling
            with adapter_type() as adapter:
                adapter.create_segment_option(application, segment,
                                              option_name)
        else:
            # TODO: format errors in a nice UI
            abort(400, "Please provide a name for the new segment option.")

        redirect(app.get_url('segments', application=application))
