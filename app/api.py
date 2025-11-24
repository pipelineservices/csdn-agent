from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel

from agent.orchestrator import Orchestrator

app = FastAPI(title="CSDN Agent API (Phase-1)")
orch = Orchestrator()


class Query(BaseModel):
    question: str


@app.post("/query")
async def query_agent(payload: Query):
    answer = orch.route(payload.question)
    return {"answer": answer}
