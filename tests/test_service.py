import json
import os
import pytest
import threading, time
from app import listen
from kafka import KafkaProducer

msg = {'test': 'aiops-qa-test'}

class Producer(threading.Thread):
    def __init__(self, server, kafka_topic, msg):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.server = server
        self.topic = kafka_topic
        self.msg = msg

    def stop(self):
        self.stop_event.set()

    def run(self):
        producer = KafkaProducer(bootstrap_servers=self.server)

        while not self.stop_event.is_set():
            producer.send(self.topic, json.dumps(self.msg).encode())
        producer.close()

@pytest.fixture
def topic():
    return os.environ.get('KAFKA_TOPIC')

@pytest.fixture
def kafka_server():
    return os.environ.get('KAFKA_SERVER')

@pytest.fixture
def producer(kafka_server, topic):
    producer = Producer(server=kafka_server, kafka_topic=topic, msg=msg)
    producer.start()
    yield
    producer.stop()

def test_kafka_listen(producer):
    for value in listen():
        if msg['test'] in str(value):
            assert True
            break
        else:
            assert time.time > 10, 'Kafka consumer failed to read message!'
