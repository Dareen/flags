import logging

from bottle import Bottle, run
from envparse import env
import newrelic.agent

from flags.views.api import APIView
from flags.views.ui import register_ui_views
from flags.conf import settings


logger = logging.getLogger(__name__)

application = Bottle()

APIView.register(application)
if settings.ADMIN_MODE:
    register_ui_views(application)


@application.route("/check")
def check():
    return "Up and running :)"


if __name__ == "__main__":
    app_kwargs = {
        "host": settings.HOST,
        "port": settings.PORT,
        "debug": settings.DEBUG,
        "reloader": settings.DEBUG
    }

    logger.info("Starting Flags with: \n%s" % "\n".join([
        "%s: %s" % (key, value) for key, value in app_kwargs.items()
    ]))

    run(application, **app_kwargs)

# wrap the bottle app with newrelic wrapper
if settings.PRODUCTION_MODE:
    # Get New Relic license key
    try:
        new_relic_license_key = env('NEW_RELIC_LICENSE_KEY')
    except KeyError:
        raise ValueError(
            "Set New Relic license key in your environment variable "
            "NEW_RELIC_LICENSE_KEY"
        )

    newrelic.agent.initialize(settings.NEW_RELIC_CONFIG)
    application = newrelic.agent.WSGIApplicationWrapper(application)
