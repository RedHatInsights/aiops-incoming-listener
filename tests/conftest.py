import asyncio
from imp import reload
from datetime import datetime

import pytest
from aiohttp import web
from aiokafka import ConsumerRecord
import asynctest

import kafka_app as original_app


@pytest.fixture
def app(request, monkeypatch):
    """Set up environment and load app module."""
    # If param is provided, it means different path is being accessed.
    path = getattr(request, 'param', '')
    # Patch environment
    monkeypatch.setenv('NEXT_SERVICE_URL', f'http://localhost:5001/{path}')
    monkeypatch.setenv('KAFKA_SERVER', 'localhost:5002')
    monkeypatch.setenv('KAFKA_TOPIC', 'STUB_TOPIC')
    monkeypatch.setenv('KAFKA_CLIENT_GROUP', 'STUB_GROUP')

    # Setup new asyncio loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    monkeypatch.setattr('kafka_app.MAIN_LOOP', loop)

    # Reload app module to propagate env. changes
    reload(original_app)

    yield original_app
    loop.close()


@pytest.fixture
async def stub_server(request, aiohttp_server):
    """Create a test server."""
    output = dict(requests=[])

    async def handler(_):
        """Test server endpoint handler."""
        resp = getattr(request, 'param', dict(body=b'Success'))
        return web.Response(**resp)

    @web.middleware
    async def any_request_middleware(request, handler):
        """Middleware storing all requests for later use."""
        output['requests'].append({
            'raw': request,
            'content': await request.json()
        })
        response = await handler(request)
        return response

    # Set up a test server
    web_app = web.Application(middlewares=[any_request_middleware])
    web_app.router.add_post('/', handler)
    server = await aiohttp_server(web_app, port=5001)

    # Store the server in fixture
    output['server'] = server
    yield output


@pytest.fixture(params=(
    b'{"url":"http://VALID_MESSAGE","b64_identity":"abcd"}',
))
def message(request):
    """Kafka message fixture."""
    return ConsumerRecord(
        'topic', 0, 0, datetime.now(), '', '', request.param, '', '', '', ()
    )


@pytest.fixture(params=(list(),))
def kafka_consumer(request, mocker):
    """Mock AIOKafkaConsumer.

    Creates a mock for AIOKafkaConsumer with patched:
    - start()
    - stop()
    - consumed message list (taken from `request.param`)
    """
    consumer = mocker.patch('kafka_app.AIOKafkaConsumer',
                            new_callable=asynctest.MagicMock)

    f_start = asyncio.Future()
    consumer.return_value.start.return_value = f_start
    f_start.set_result(True)
    consumer.return_value.__aiter__.return_value = request.param
    f_stop = asyncio.Future()
    consumer.return_value.stop.return_value = f_stop
    f_stop.set_result(True)

    yield consumer


@pytest.fixture()
async def kafka_consumer_start():
    """Mock AIOKafkaConsumer as Subscribed and Active."""
    await original_app.consume_messages()
    return True
