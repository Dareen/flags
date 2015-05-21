#
#  Part of the python-bottle-skeleton project at:
#
#      https://github.com/linsomniac/python-bottle-skeleton
#
import os

from bottle import (view, TEMPLATE_PATH, Bottle, static_file, request,
                    redirect, BaseTemplate)

#  XXX Remove these lines and the next section if you aren't processing forms
from wtforms import Form, TextField, validators


#  XXX Form validation example
# class NewUserFormProcessor(Form):
#     name = TextField('Username', [validators.Length(min=4, max=25)])
#     full_name = TextField('Full Name', [validators.Length(min=4, max=60)])
#     email_address = TextField(
#             'Email Address', [validators.Length(min=6, max=35)])
#     password = PasswordField(
#             'New Password',
#             [validators.Required(),
#                 validators.EqualTo('confirm',
#                     message='Passwords must match')
#             ])
#     confirm = PasswordField('Repeat Password')


def register_ui_views(app):

    #  Pretty much this entire function needs to be written for your

    # Template global variable
    # BaseTemplate.defaults['app'] = app
    # Location of HTML templates
    TEMPLATE_PATH.insert(0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../templates'))
    )

    #  XXX Index page
    @app.route('/', name='index')
    @view('index')  # Name of template
    def index():

        flags = {
            "TEST": "1",
        }

        #  any local variables can be used in the template
        return locals()
