import os
from pytest_mock import mocker

payload = {'test': 'aiops'}

def test_listen(mocker, app):
    app.KafkaConsumer = mocker.MagicMock()
    message = app.listen()
    try:
        next(message)
    except StopIteration:
        app.KafkaConsumer.assert_called_once()

def test_hit_next_in_pipepine_request(mocker, app):
    host = os.environ.get('NEXT_MICROSERVICE_HOST')
    app.requests.post = mocker.MagicMock()
    # app.requests.post.return_value = responses.mock.POST
    app.hit_next_in_pipepine(payload)
    app.requests.post.assert_called_once()
