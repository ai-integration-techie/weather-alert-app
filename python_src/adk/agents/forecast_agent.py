from google_adk.agents import LlmAgent
from python_src.adk.tools.forecast_tools import get_weather_forecast


class ForecastAgent(LlmAgent):
    def __init__(self, model: str = "gemini-pro"):
        super().__init__(
            tools=[get_weather_forecast],
            model=model,
        )
