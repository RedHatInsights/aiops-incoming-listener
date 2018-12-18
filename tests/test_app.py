import pytest
from pytest_mock import mocker

def test_listen(mocker, app):
    app.KafkaConsumer = mocker.MagicMock()
    message = app.listen()
    try:
        next(message)
    except StopIteration:
        app.KafkaConsumer.assert_called_once()

def test_hit_next_in_pipepine_request(mocker, app):
    payload = {'test': 'aiops'}
    app.requests.post = mocker.MagicMock()
    app.hit_next_in_pipepine(payload)
    app.requests.post.assert_called_once()
