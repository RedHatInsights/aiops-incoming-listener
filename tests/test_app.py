import pytest
from aiohttp import ClientResponseError, ClientConnectionError


@pytest.mark.asyncio
class TestHitNext:
    """Test. `hit_next` function."""

    async def test_server_available(self, app, stub_server):
        """Server is available, any message should get accepted."""
        resp = await app.hit_next('STUB_ID', {'url': 'http://STUB.URL'})
        first_request = stub_server['requests'][0]

        assert len(stub_server['requests']) == 1
        assert first_request['raw'].method == 'POST'
        assert first_request['content']['url'] == 'http://STUB.URL'
        assert first_request['content']['origin'] == 'STUB_TOPIC'
        assert resp.status == 200

    async def test_forward_rh_account(self, app, stub_server):
        """Provide 'rh_account' in metadata."""
        resp = await app.hit_next(
            'STUB_ID',
            {'url': 'http://STUB.URL', 'rh_account': 'STUB_ACCOUNT'}
        )
        request = stub_server['requests'][0]

        assert request['content']['metadata']['rh_account'] == 'STUB_ACCOUNT'
        assert resp.status == 200

    @pytest.mark.parametrize('app', ['INVALID_ENDPOINT'], indirect=True)
    @pytest.mark.parametrize('stub_server', [{'status': 404}], indirect=True)
    async def test_invalid_endpoint(self, app, stub_server):
        """Hit invalid endpoint."""
        with pytest.raises(ClientResponseError) as err:
            await app.hit_next('STUB_ID', {'url': 'http://STUB.URL'})
            assert err.status == 404

        assert len(stub_server['requests']) == app.MAX_RETRIES
        for req in stub_server['requests']:
            assert req['raw'].method == 'POST'
            assert str(req['raw'].rel_url) == '/INVALID_ENDPOINT'

    async def test_invalid_server(self, app):
        """Server doesn't exist."""
        with pytest.raises(ClientConnectionError):
            await app.hit_next('STUB_ID', {'url': 'http://STUB.URL'})


# class ProcessMessage(Object):
#     pass

# class ConsumeMessages(Object):
#     pass
