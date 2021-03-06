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

    # TODO: format errors in a nice UI instead of abort

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
            application_name = request.forms.new_application
            if application_name:
                try:
                    with adapter_type() as adapter:
                        adapter.create_application(application_name)
                except KeyExistsError:
                    abort(409, "Application %s already exists." %
                          application_name)
            else:
                abort(400, "Please provide a name for the new application.")

        default = "Enabled" if settings.DEFAULT_VALUE else "Disabled"
        with adapter_type() as adapter:
            applications = adapter.get_applications()

        #  any local variables can be used in the template
        return locals()

    @app.route('/<application_name>/features', name='features',
               method=["GET", "POST"])
    @view('features')  # Name of template
    def features(application_name):
        application_name = application_name.lower()
        saved = False
        added = False
        error = None
        abort = False

        if request.method == "POST":
            feature_chck_name_tmpl = "%s_checkbox"
            segment_chck_name_tmpl = "%s_%s_checkbox"
            option_chck_name_tmpl = "%s_%s_%s_checkbox"

            with adapter_type() as adapter:
                segments = adapter.get_all_segments(application_name)
                features = adapter.get_all_features(application_name)

                for feature in features:
                    # a checkbox is checked if it exists in request.forms
                    feature_dict = {
                        "feature_toggled": True if request.forms.get(
                            feature_chck_name_tmpl % feature
                        ) else False,
                        "segmentation": {
                            segment: {
                                "toggled": True if request.forms.get(
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
                    adapter.update_feature(application_name, feature,
                                           feature_dict)
                    saved = True

        default = "Enabled" if settings.DEFAULT_VALUE else "Disabled"
        try:
            with adapter_type() as adapter:
                features = adapter.get_all_features(application_name)
        except KeyDoesNotExistError:
            error = "Application %s does not exist." % application_name
            abort = True

        #  any local variables can be used in the template
        return locals()

    # TODO: change this crappy URL later
    @app.post('/<application_name>/create', name='create')
    @view('features')  # Name of template
    def create_feature(application_name):
        application_name = application_name.lower()
        feature_name = request.forms.new_feature
        added = False
        saved = False
        error = None
        abort = False

        if feature_name:
            try:
                with adapter_type() as adapter:
                    adapter.create_feature(application_name, feature_name)
                added = True
            except KeyExistsError:
                error = ("Feature %s already exists for application %s." %
                         (feature_name, application_name))

        else:
            error = "Please provide a name for the new feature."

        # TODO: redirect to features instead of this block
        default = "Enabled" if settings.DEFAULT_VALUE else "Disabled"
        try:
            with adapter_type() as adapter:
                features = adapter.get_all_features(application_name)
        except KeyDoesNotExistError:
            error = "Application %s does not exist." % application_name
            abort = True

        #  any local variables can be used in the template
        return locals()

    @app.route('/<application_name>/segments', name='segments',
               method=["GET", "POST"])
    @view('segments')  # Name of template
    def segments(application_name):
        application_name = application_name.lower()
        if request.method == "POST":
            segment_name = request.forms.new_segment
            if segment_name:
                try:
                    with adapter_type() as adapter:
                        adapter.create_segment(application_name, segment_name)
                except KeyExistsError:
                    abort(409, "Segment %s already exists for application %s."
                          % (segment_name, application_name))
            else:
                abort(400, "Please provide a name for the new segment.")

        try:
            with adapter_type() as adapter:
                segments = adapter.get_all_segments(application_name)
        except KeyDoesNotExistError:
            abort(404, "Application %s does not exist." % application_name)

        #  any local variables can be used in the template
        return locals()

    @app.post('/<application_name>/options/<segment>', name='options')
    def options(application_name, segment):
        option_name = request.forms.new_option
        if option_name:
            try:
                with adapter_type() as adapter:
                    adapter.create_segment_option(application_name, segment,
                                                  option_name)
            except KeyExistsError:
                    abort(409, "Option %s already exists for segment %s in "
                          "application %s." % (option_name, segment,
                                               application_name))
        else:
            abort(400, "Please provide a name for the new segment option.")

        redirect(app.get_url('segments', application_name=application_name))
