from google_adk.agents import LlmAgent
from python_src.adk.tools.data_tools import query_historical_storms


class DataAgent(LlmAgent):
    def __init__(self, model: str = "gemini-pro"):
        super().__init__(
            tools=[query_historical_storms],
            model=model,
        )
