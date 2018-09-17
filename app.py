import os
from time import sleep
import logging
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO)

KAFKA_SERVER = os.environ.get('KAFKA_SERVER')
TOPIC = os.environ.get('TOPIC')

def consumer():
    logging.info(f'Connecting to Kafka server ({KAFKA_SERVER})')
    logging.info(f'Subscribing to topic: "{TOPIC}"')
    consumer = KafkaConsumer(TOPIC, bootstrap_servers=KAFKA_SERVER)

    for msg in consumer:
        logging.info("Receiving message:")
        logging.info(msg)


if __name__ == '__main__':
    consumer()
