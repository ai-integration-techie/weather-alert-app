from google_adk.tools import tool


@tool
def correlate_data(historical_data: dict, forecast_data: dict) -> dict:
    """Correlates historical data with current forecasts for risk assessment."""
    # For this example, we'll just return a simple correlation.
    if historical_data.get("results") and forecast_data.get("properties"):
        return {
            "correlation": "There is a high correlation between the historical data and the forecast."
        }
    return {"correlation": "Could not determine correlation."}
