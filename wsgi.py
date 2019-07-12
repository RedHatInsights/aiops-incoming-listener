import logging
import os
import threading

from flask import Flask, jsonify

import kafka_app as APP


gunicorn_logger = logging.getLogger('gunicorn.error')


# W0212 Access to a protected member _conns of a client class [pylint]
# pylint: disable=W0212


def create_application():
    """Create App."""
    app = Flask(__name__)
    thread = threading.Thread(target=APP.main)
    thread.start()

    return app


application = create_application()


@application.route("/", methods=['GET'])
def get_root():
    """Root Endpoint."""
    if APP.KAFKA_RESOURCES.get('consumer') and \
            APP.KAFKA_RESOURCES.get('consumer')._client._conns:
        return jsonify(
            status='OK',
            message='Listener Up and Running'
        )
    return jsonify(
        status='Error',
        message='Listener Down'
    ), 500


if __name__ == '__main__':
    # pylama:ignore=C0103
    port = os.environ.get("PORT", 8004)
    application.run(port=int(port))
