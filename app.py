import os
import logging
import sys
from json import loads

from kafka import KafkaConsumer
import requests

# Setup logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('consumer')
logger.setLevel(logging.INFO)


def hit_next_in_pipepine(payload: dict) -> None:
    """Pass the data to next service in line."""
    host = os.environ.get('NEXT_MICROSERVICE_HOST')

    # FIXME: Convert to aiohttp or some other async requests alternative
    # Do not wait for response now, so we can keep listening
    try:
        requests.post(f'http://{host}', json=payload, timeout=10)
    except requests.exceptions.ReadTimeout:
        pass
    except requests.exceptions.ConnectionError as e:
        logger.warning('Call to next service failed: %s', str(e))


def listen() -> dict:
    """Kafka messages listener.

    Connects to Kafka server, consumes a topic and yields every message it
    receives.
    """
    server = os.environ.get('KAFKA_SERVER')
    topic = os.environ.get('KAFKA_CONSUMER_TOPIC')

    logger.info('Connecting to Kafka server (%s)', server)
    logger.info('Subscribing to topic: "%s"', topic)

    consumer = KafkaConsumer(topic, bootstrap_servers=server)

    for msg in consumer:
        logger.debug('Received message: %s', str(msg))
        yield loads(msg.value)


if __name__ == '__main__':
    # Check environment variables passed to container
    # pylama:ignore=C0103
    env = {'KAFKA_SERVER', 'KAFKA_CONSUMER_TOPIC', 'NEXT_MICROSERVICE_HOST'}

    if not env.issubset(os.environ):
        logger.error(
            'Environment not set properly, missing %s',
            env - set(os.environ)
        )
        sys.exit(1)

    # Run the consumer
    for received in listen():
        if 'url' not in received:
            logger.warning(
                'Message is missing data location URL. Message ignored: %s',
                received
            )
            continue

        message = {
            'url': received.get('url'),
            'origin': 'kafka',
            'metadata': {
                'rh_account': received.get('rh_account', None)
            }
        }

        hit_next_in_pipepine(message)
