import os
import pytest
from pytest_mock import mocker

@pytest.fixture
def env():
    """This fixture contains the dict of environment variables that are required."""
    return {
        "KAFKA_SERVER": "localhost:9092",
        "KAFKA_TOPIC": "aiosp-topic",
        "KAFKA_CLIENT_GROUP": "aiops_group",
        "NEXT_MICROSERVICE_HOST": "localhost:9092"
    }

@pytest.fixture
def app(mocker, env):
    """This fixture contain the instance of app module after setting up the environment variables."""
    mocker.patch.dict(os.environ, env)
    import app
    yield app
