#
#  Part of the python-bottle-skeleton project at:
#
#      https://github.com/linsomniac/python-bottle-skeleton
#
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

    # Index page: list of available applications
    @app.route('/', name='index')
    @view('index')  # Name of template
    def index():
        default = settings.DEFAULT_VALUE
        with adapter_type() as adapter:
            applications = adapter.get_applications()

        #  any local variables can be used in the template
        return locals()

    @app.get('/<application>', name='flags')
    @app.post('/<application>')
    @view('flags')  # Name of template
    def flags(application):
        def post():
            # TODO
            application = request.forms
            redirect(app.get_url('index'))

        if request.method == "POST":
            post()

        default = settings.DEFAULT_VALUE

        with adapter_type() as adapter:
            flags = adapter.get_all_items(application)

        #  any local variables can be used in the template
        return locals()
