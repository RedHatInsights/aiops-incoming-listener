import os
from time import sleep
import logging
from kafka import KafkaConsumer

# Setup logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('consumer')
logger.setLevel(logging.INFO)

def consumer(server, topic):
    '''
    Simple Kafka consumer

    Connects to Kafka server, consumes a topic and yields every message it
    receives.
    '''
    logger.info(f'Connecting to Kafka server ({server})')
    logger.info(f'Subscribing to topic: "{topic}"')
    consumer = KafkaConsumer(topic, bootstrap_servers=server)

    [logger.info(msg) for msg in consumer]


if __name__ == '__main__':
    # Env. variables passed to container
    kafka_server = os.environ.get('KAFKA_SERVER')
    topic = os.environ.get('TOPIC')

    # Run the consumer
    consumer(kafka_server, topic)
