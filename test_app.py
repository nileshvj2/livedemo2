import pytest
import requests
from unittest.mock import patch, MagicMock, call

from app import get_weather, MAX_RETRIES


@pytest.fixture
def mock_weather_response():
    mock = MagicMock()
    mock.json.return_value = {
        "main": {"temp": 295.15, "humidity": 60, "pressure": 1013},
        "weather": [{"description": "clear sky"}],
        "wind": {"speed": 5.1},
        "sys": {"country": "GB"},
        "name": "London",
    }
    return mock


def test_get_weather_returns_dict(mock_weather_response):
    with patch("app.requests.get", return_value=mock_weather_response):
        result = get_weather("London")
    assert isinstance(result, dict)


def test_get_weather_contains_main_key(mock_weather_response):
    with patch("app.requests.get", return_value=mock_weather_response):
        result = get_weather("London")
    assert "main" in result


def test_get_weather_temp_value(mock_weather_response):
    with patch("app.requests.get", return_value=mock_weather_response):
        result = get_weather("London")
    assert result["main"]["temp"] == 295.15


def test_get_weather_calls_correct_url(mock_weather_response):
    with patch("app.requests.get", return_value=mock_weather_response) as mock_get:
        get_weather("Tokyo")
    call_args = mock_get.call_args
    assert "openweathermap.org" in call_args[0][0]
    assert call_args[1]["params"]["q"] == "Tokyo"


def test_get_weather_uses_api_key_from_env(mock_weather_response):
    with patch("app.os.getenv", return_value="test-api-key"):
        with patch("app.requests.get", return_value=mock_weather_response) as mock_get:
            get_weather("Paris")
    assert mock_get.call_args[1]["params"]["appid"] == "test-api-key"


def test_get_weather_missing_api_key(mock_weather_response):
    with patch("app.os.getenv", return_value=None):
        with patch("app.requests.get", return_value=mock_weather_response) as mock_get:
            get_weather("Berlin")
    assert mock_get.call_args[1]["params"]["appid"] is None


def test_get_weather_network_error():
    with patch("app.requests.get", side_effect=requests.exceptions.ConnectionError):
        with patch("app.time.sleep"):
            with pytest.raises(requests.exceptions.ConnectionError):
                get_weather("London")


def test_get_weather_calls_response_json(mock_weather_response):
    with patch("app.requests.get", return_value=mock_weather_response):
        get_weather("London")
    mock_weather_response.json.assert_called_once()


def test_get_weather_retries_on_connection_error(mock_weather_response):
    """Fails twice, succeeds on third attempt."""
    with patch(
        "app.requests.get",
        side_effect=[
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectionError,
            mock_weather_response,
        ],
    ) as mock_get:
        with patch("app.time.sleep"):
            result = get_weather("London")
    assert mock_get.call_count == 3
    assert isinstance(result, dict)


def test_get_weather_exhausts_all_retries():
    """Raises after MAX_RETRIES consecutive failures."""
    with patch(
        "app.requests.get",
        side_effect=requests.exceptions.ConnectionError,
    ) as mock_get:
        with patch("app.time.sleep"):
            with pytest.raises(requests.exceptions.ConnectionError):
                get_weather("London")
    assert mock_get.call_count == MAX_RETRIES


def test_get_weather_exponential_backoff():
    """Sleep durations follow 2^attempt: 1s, 2s on first two failures."""
    with patch(
        "app.requests.get",
        side_effect=[
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectionError,
            MagicMock(**{"json.return_value": {"main": {"temp": 300}}}),
        ],
    ):
        with patch("app.time.sleep") as mock_sleep:
            get_weather("London")
    mock_sleep.assert_has_calls([call(1), call(2)])


def test_get_weather_no_retry_on_success(mock_weather_response):
    """Succeeds on first attempt — sleep is never called."""
    with patch("app.requests.get", return_value=mock_weather_response):
        with patch("app.time.sleep") as mock_sleep:
            get_weather("London")
    mock_sleep.assert_not_called()
