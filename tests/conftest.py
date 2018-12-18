import os, pytest

@pytest.fixture
def env():
    return {
        "KAFKA_SERVER": "localhost:9092",
        "KAFKA_TOPIC": "aiosp-topic",
        "KAFKA_CLIENT_GROUP": "aiops_group",
        "NEXT_MICROSERVICE_HOST": "localhost:9092"
    }

@pytest.fixture
def app(mocker, monkeypatch, env):
    mocker.patch.dict(os.environ, env)
    import app
    yield app
