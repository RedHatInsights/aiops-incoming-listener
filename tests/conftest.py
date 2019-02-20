import asyncio
from imp import reload
from datetime import datetime

import pytest
from aiohttp import web
from aiokafka import ConsumerRecord


import app as original_app


@pytest.fixture
def app(request, monkeypatch):
    """Set up environment and load app module."""
    # If param is provided, it means different path is being accessed.
    path = request.param if hasattr(request, 'param') else str()
    # Patch environment
    monkeypatch.setenv('NEXT_MICROSERVICE_HOST', f'localhost:5001/{path}')
    monkeypatch.setenv('KAFKA_SERVER', 'localhost:5002')
    monkeypatch.setenv('KAFKA_TOPIC', 'STUB_TOPIC')
    monkeypatch.setenv('KAFKA_CLIENT_GROUP', 'STUB_GROUP')

    # Setup new asyncio loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Reload app module to propagate env. changes
    reload(original_app)

    yield original_app


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


@pytest.fixture(params=(b'{"url":"http://VALID_MESSAGE"}',))
def message(request):
    """Kafka message fixture."""
    return ConsumerRecord(
        'topic', 0, 0, datetime.now(), '', '', request.param, '', '', ''
    )
