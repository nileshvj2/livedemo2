# Fetch current weather data for a given city from OpenWeatherMap API

import os
import time

import requests

MAX_RETRIES = 3


def get_weather(city: str) -> dict:
    """
    Fetch current weather data for a given city from the OpenWeatherMap API.

    Retries up to 3 times with exponential backoff on connection errors.

    Args:
        city (str): The name of the city (e.g., "London", "Tokyo").

    Returns:
        dict: The full JSON response from OpenWeatherMap, including keys such as
              ``main`` (temp, humidity, pressure), ``weather`` (description),
              ``wind``, and ``sys``. Temperatures are in Kelvin by default.

    Raises:
        requests.exceptions.ConnectionError: If all retries are exhausted.
        requests.exceptions.HTTPError: If the API returns a non-2xx status code.

    Example:
        >>> data = get_weather("London")
        >>> temp_kelvin = data["main"]["temp"]
    """
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": os.getenv("WEATHER_API_KEY")
    }
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params)
            return response.json()
        except requests.exceptions.ConnectionError as e:
            last_error = e
            time.sleep(2 ** attempt)
    raise last_error


def get_forecast(city: str) -> dict:
    """
    Fetch a 5-day / 3-hour forecast for a given city from the OpenWeatherMap API.

    Retries up to 3 times with exponential backoff on connection errors.

    Args:
        city (str): The name of the city (e.g., "London", "Tokyo").

    Returns:
        dict: The full JSON forecast response containing a ``list`` of up to
              40 forecast entries, each with ``dt_txt``, ``main``, and
              ``weather`` keys.

    Raises:
        requests.exceptions.ConnectionError: If all retries are exhausted.
        requests.exceptions.HTTPError: If the API returns a non-2xx status code.
    """
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": os.getenv("WEATHER_API_KEY")
    }
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params)
            return response.json()
        except requests.exceptions.ConnectionError as e:
            last_error = e
            time.sleep(2 ** attempt)
    raise last_error