import os
import logging
from kafka import KafkaConsumer

# Setup logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('consumer')
logger.setLevel(logging.INFO)


def listen(server: str, topic: str) -> None:
    """Kafka messages listener.

    Connects to Kafka server, consumes a topic and yields every message it
    receives.
    """
    logger.info('Connecting to Kafka server (%s)', server)
    logger.info('Subscribing to topic: "%s"', topic)
    consumer = KafkaConsumer(topic, bootstrap_servers=server)

    # pylama:ignore=W0106
    [logger.info(msg) for msg in consumer]


if __name__ == '__main__':
    # Env. variables passed to container
    KAFKA_SERVER = os.environ.get('KAFKA_SERVER')
    KAFKA_TOPIC = os.environ.get('TOPIC')

    # Run the consumer
    listen(KAFKA_SERVER, KAFKA_TOPIC)
