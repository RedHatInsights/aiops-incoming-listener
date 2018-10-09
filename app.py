import os
import logging
from json import loads

from kafka import KafkaConsumer
import requests

# Setup logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('consumer')
logger.setLevel(logging.INFO)


def hit_next_in_pipepine(url: str, payload: dict) -> None:
    """Pass the data to next service in line."""
    # Do not wait for response now, so we can keep listening
    # FIXME: Convert to aiohttp or some other async requests alternative
    try:
        requests.post(url, json=payload, timeout=10)
    except requests.exceptions.ReadTimeout:
        pass
    except requests.exceptions.ConnectionError as e:
        logger.warning('Call to next service failed: %s', str(e))


def listen(server: str, topic: str) -> dict:
    """Kafka messages listener.

    Connects to Kafka server, consumes a topic and yields every message it
    receives.
    """
    logger.info('Connecting to Kafka server (%s)', server)
    logger.info('Subscribing to topic: "%s"', topic)
    consumer = KafkaConsumer(topic, bootstrap_servers=server)

    for msg in consumer:
        logger.debug('Received message: %s', str(msg))
        yield loads(msg.value)


if __name__ == '__main__':
    # Env. variables passed to container
    KAFKA_SERVER = os.environ.get('KAFKA_SERVER')
    KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC')
    NEXT_MICROSERVICE_URL = os.environ.get('NEXT_MICROSERVICE_URL')

    # Run the consumer
    for received in listen(KAFKA_SERVER, KAFKA_TOPIC):
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

        hit_next_in_pipepine(NEXT_MICROSERVICE_URL, message)
