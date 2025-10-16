from google_adk.tools import tool
import httpx

from python_src.config.environment import config


@tool
def get_weather_forecast(location: str) -> dict:
    """Gets the weather forecast for a given location."""
    try:
        # Use a geocoding service to get the latitude and longitude of the location.
        # For this example, we'll use a hardcoded location.
        latitude = 32.7767
        longitude = -96.7970

        # Get the weather forecast from the National Weather Service API.
        client = httpx.AsyncClient(
            base_url=config.NWS_BASE_URL,
            headers={"User-Agent": config.NWS_USER_AGENT},
            timeout=10.0
        )
        response = client.get(f"/points/{latitude},{longitude}")
        response.raise_for_status()
        forecast_url = response.json()["properties"]["forecast"]
        response = client.get(forecast_url)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
