from fastapi import FastAPI
from pydantic import BaseModel
from python_src.adk.orchestrator.adk_orchestrator import run

app = FastAPI()


class Request(BaseModel):
    prompt: str


@app.post("/run")
def run_agent(request: Request):
    return {"response": run(request.prompt)}
