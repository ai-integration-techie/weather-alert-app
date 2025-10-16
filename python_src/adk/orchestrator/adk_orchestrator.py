from google_adk.runners import Runner
from python_src.adk.agents.root_agent import RootAgent


def run(prompt: str):
    runner = Runner(RootAgent())
    return runner.run(prompt)
