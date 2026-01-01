import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import httpx
from services.data_poller import fetch_data, poll_data_services

@pytest.mark.asyncio
async def test_fetch_data_success():
    # Mock the client and response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"key": "value"}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    url = "http://test-url"
    service_name = "TestService"

    result = await fetch_data(mock_client, url, service_name)

    mock_client.get.assert_called_once_with(url)
    assert result == {"key": "value"}

@pytest.mark.asyncio
async def test_fetch_data_network_error():
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.RequestError("Network error", request=MagicMock())

    result = await fetch_data(mock_client, "http://test-url", "TestService")

    assert result is None

@pytest.mark.asyncio
async def test_fetch_data_http_error():
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    
    # raise_for_status should raise the HTTPStatusError
    error = httpx.HTTPStatusError("500 Error", request=MagicMock(), response=mock_response)
    mock_response.raise_for_status.side_effect = error

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    result = await fetch_data(mock_client, "http://test-url", "TestService")

    assert result is None

@pytest.mark.asyncio
async def test_fetch_data_unexpected_error():
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = Exception("Unexpected")

    result = await fetch_data(mock_client, "http://test-url", "TestService")

    assert result is None

@pytest.mark.asyncio
async def test_poll_data_services_runs_cycle():
    # We poll poll_data_services, but since it has a while True, 
    # we need to interrupt it. A clean way is to mock asyncio.sleep 
    # to raise a CancelledError or similar exception after 1 call to break the loop.
    
    with patch("services.data_poller.httpx.AsyncClient") as mock_client_cls, \
         patch("services.data_poller.fetch_data") as mock_fetch, \
         patch("asyncio.sleep", side_effect=Exception("StopLoop")) as mock_sleep:
        
        mock_client_instance = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client_instance

        try:
            await poll_data_services()
        except Exception as e:
            assert str(e) == "StopLoop"

        # Verify fetch_data was called twice (once for Kostal, once for Fronius)
        assert mock_fetch.call_count == 2
        # Verify sleep was called
        assert mock_sleep.called
