from google_adk.agents import LlmAgent
from python_src.adk.tools.insights_tools import correlate_data


class InsightsAgent(LlmAgent):
    def __init__(self, model: str = "gemini-pro"):
        super().__init__(
            tools=[correlate_data],
            model=model,
        )
