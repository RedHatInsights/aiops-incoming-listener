import logging
import os
import threading

from flask import Flask

import kafka_app as APP


gunicorn_logger = logging.getLogger('gunicorn.error')


def create_application():
    """Create App."""
    app = Flask(__name__)
    thread = threading.Thread(target=APP.main)
    thread.start()

    return app


application = create_application()


if __name__ == '__main__':
    # pylama:ignore=C0103
    port = os.environ.get("PORT", 8004)
    application.run(port=int(port))
