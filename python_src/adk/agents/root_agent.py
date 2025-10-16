from google_adk.agents import SequentialAgent
from python_src.adk.agents.data_agent import DataAgent
from python_src.adk.agents.forecast_agent import ForecastAgent
from python_src.adk.agents.insights_agent import InsightsAgent


class RootAgent(SequentialAgent):
    def __init__(self, model: str = "gemini-pro"):
        super().__init__(
            agents=[
                DataAgent(model=model),
                ForecastAgent(model=model),
                InsightsAgent(model=model),
            ]
        )
