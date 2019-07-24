import wsgi

# R0201 = Method could be a function Used when a method doesn't use its bound
# instance, and so could be written as a function.
# R0903 = Too few public methods
# W0212 = Access to a protected member of a client class

# pylint: disable=R0201,R0903,W0212


class TestGetRoot:
    """Test various use cases for the index route."""

    def test_route_with_consumer_started(self, mocker, app, kafka_consumer,
                                         kafka_consumer_start):
        """Test index route when consumer is subscribed."""
        client = wsgi.application.test_client(mocker)

        url = '/'

        response = client.get(url)

        output = {
            "message": "Listener Up and Running",
            "status": "OK"
        }

        assert app.__name__ == 'kafka_app'
        kafka_consumer.assert_called_once()
        assert kafka_consumer_start

        assert response.get_json() == output
        assert response.status_code == 200

    def test_route_with_consumer_not_started(self, app, mocker):
        """Test index route when consumer is not available."""
        client = wsgi.application.test_client(mocker)

        url = '/'

        response = client.get(url)

        output = {
            "message": "Listener Down",
            "status": "Error"
        }

        assert app.__name__ == 'kafka_app'
        assert response.get_json() == output
        assert response.status_code == 500

    def test_route_with_metrics(self, mocker):
        """Basic test for metrics route."""
        client = wsgi.application.test_client(mocker)

        url = '/metrics'

        response = client.get(url)

        assert response.status_code == 200
