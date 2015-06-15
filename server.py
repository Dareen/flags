import logging

from bottle import Bottle, run

from flags.api import FlagsView
from flags.conf import settings


logger = logging.getLogger(__name__)

app = Bottle()

FlagsView.register(app)


@app.route("/check")
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

    run(app, **app_kwargs)
