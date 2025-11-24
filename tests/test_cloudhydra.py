from services.cloudhydra_service import get_cloudhydra_runbook


def test_runbook_loads():
    text = get_cloudhydra_runbook()
    assert "Cloudhydra" in text or text != ""
    
    # tests/test_cloudhydra.py

from agent.cloudhydra_agent import CloudhydraAgent
from models.shared import LLMClient
from pipeline.memory import ConversationMemory


def test_cloudhydra_phase2_smoke():
    llm = LLMClient()
    mem = ConversationMemory()
    agent = CloudhydraAgent(llm, mem)

    resp = agent.handle("Network is slow between Databricks and Aurora. What should we check?")
    assert isinstance(resp, str)
    assert "Summary" in resp or "summary" in resp

