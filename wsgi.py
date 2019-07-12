import logging
import os
import sys
import threading

from flask import Flask, jsonify


from gunicorn.arbiter import Arbiter


gunicorn_logger = logging.getLogger('gunicorn.error')

# all gunicorn processes in a given instance need to access a common
# folder in /tmp where the metrics can be recorded
PROMETHEUS_MULTIPROC_DIR = '/tmp/aiops_incoming_listener'

try:
    os.makedirs(PROMETHEUS_MULTIPROC_DIR, exist_ok=True)
    os.environ['prometheus_multiproc_dir'] = PROMETHEUS_MULTIPROC_DIR
    import kafka_app as APP
except IOError as e:
    # this is a non-starter for scraping metrics in the
    # Multiprocess Mode (Gunicorn)
    # terminate if there is an exception here
    gunicorn_logger.error(
        "Error while creating prometheus_multiproc_dir: %s", e
    )
    sys.exit(Arbiter.APP_LOAD_ERROR)


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


@application.route("/metrics", methods=['GET'])
def get_metrics():
    """Metrics Endpoint."""
    return APP.metrics()


if __name__ == '__main__':
    # pylama:ignore=C0103
    port = os.environ.get("PORT", 8004)
    application.run(port=int(port))
