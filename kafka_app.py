import os
import logging
import sys
from json import loads
from uuid import uuid4
import asyncio

import aiohttp
from aiokafka import AIOKafkaConsumer, ConsumerRecord

# Setup logging
logging.basicConfig(
    level=logging.WARNING,
    format=(
        "[%(asctime)s] %(levelname)s "
        "[%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    )
)
logger = logging.getLogger('consumer')
logger.setLevel(logging.DEBUG)

# Globals
# Asynchronous event loop
MAIN_LOOP = asyncio.get_event_loop()

# Kafka listener config
SERVER = os.environ.get('KAFKA_SERVER')
TOPIC = os.environ.get('KAFKA_TOPIC')
GROUP_ID = os.environ.get('KAFKA_CLIENT_GROUP')
CLIENT_ID = uuid4()

# Properties required to be present in a message
VALIDATE_PRESENCE = {'url', 'b64_identity'}

# Next micro-service host:port
NEXT_SERVICE_URL = os.environ.get('NEXT_SERVICE_URL')
MAX_RETRIES = 3

KAFKA_RESOURCES = {}


async def hit_next(msg_id: str, message: dict) -> aiohttp.ClientResponse:
    """Send message as JSON to the HOST via HTTP Post.

    Perform a async HTTP post call to the next micro-service endpoint
    specified via NEXT_SERVICE_URL env. variable.
    The message is serialized as JSON
    :param msg_id: Message identifier used in logs
    :param message: A dictionary sent as a payload
    :return: HTTP response
    """
    # Basic response
    output = {
        'url': message.get('url'),
        'origin': TOPIC
    }

    # Additional data
    if message.get('rh_account'):
        output['metadata'] = {
            'rh_account': message.get('rh_account')
        }

    # b64_identity
    b64_identity = message.get('b64_identity', '')

    # Pass data to the next microservice
    logger.debug('Message %s: forwarding...', msg_id)
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        for attempt in range(MAX_RETRIES):
            try:
                resp = await session.post(
                    NEXT_SERVICE_URL,
                    headers={"x-rh-identity": b64_identity},
                    json=output
                )
                logger.debug('Message %s: sent', msg_id)
                break
            except aiohttp.ClientError as e:
                logging.warning(
                    'Async request failed (attempt #%d), retrying: %s',
                    attempt, str(e)
                )
                resp = e
        else:
            logging.error('All attempts failed!')
            raise resp
    return resp


async def process_message(message: ConsumerRecord) -> bool:
    """Take a message and process it.

    Parse the collected message and check if it's in valid for. If so,
    validate it contains the data we're interested in and pass it to next
    service in line.
    :param message: Raw Kafka message which should be interpreted
    :return: Success of processing
    """
    msg_id = f'#{message.partition}_{message.offset}'
    logger.debug("Message %s: parsing...", msg_id)

    # Parse the message as JSON
    try:
        message = loads(message.value)
    except ValueError as e:
        logger.error(
            'Unable to parse message %s: %s',
            str(message), str(e)
        )
        return False

    logger.debug('Message %s: %s', msg_id, str(message))

    # Select only the interesting messages
    if not all(message.get(k) for k in VALIDATE_PRESENCE):
        return False

    try:
        await hit_next(msg_id, message)
    except aiohttp.ClientError:
        logger.warning('Message %s: Unable to pass message', msg_id)
        return False

    logger.info('Message %s: Done', msg_id)
    return True


async def consume_messages() -> None:
    """Listen to Kafka topic and fetch messages.

    Connects to Kafka server, consumes a topic and schedules a task for
    processing the message.
    :return None
    """
    logger.info('Connecting to Kafka server...')
    logger.info('Client configuration:')
    logger.info('\tserver:    %s', SERVER)
    logger.info('\ttopic:     %s', TOPIC)
    logger.info('\tgroup_id:  %s', GROUP_ID)
    logger.info('\tclient_id: %s', CLIENT_ID)

    consumer = AIOKafkaConsumer(
        TOPIC,
        loop=MAIN_LOOP,
        client_id=CLIENT_ID,
        group_id=GROUP_ID,
        bootstrap_servers=SERVER
    )

    # Get cluster layout, subscribe to group
    await consumer.start()
    KAFKA_RESOURCES['consumer'] = consumer
    logger.info('Consumer subscribed and active!')

    # Start consuming messages
    try:
        async for msg in consumer:
            logger.debug('Received message: %s', str(msg))
            MAIN_LOOP.create_task(process_message(msg))

    finally:
        await consumer.stop()


def main():
    """Service init function."""
    if __name__ == 'kafka_app':
        # Check environment variables passed to container
        # pylama:ignore=C0103
        env = {'KAFKA_SERVER', 'KAFKA_TOPIC', 'NEXT_SERVICE_URL'}

        if not env.issubset(os.environ):
            logger.error(
                'Environment not set properly, missing %s',
                env - set(os.environ)
            )
            sys.exit(1)

        # Run the consumer
        MAIN_LOOP.run_until_complete(consume_messages())
