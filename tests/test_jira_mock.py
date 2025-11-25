# tests/test_jira_mock.py

from services.jira_client import JiraClient
from agent.jira_agent import JiraAgent
from agent.orchestrator import Orchestrator
from models.shared import LLMClient
from pipeline.memory import ConversationMemory


def test_jira_client_create_issue():
    client = JiraClient()
    issue = client.create_issue("Test issue", "Details", "high")

    assert issue["key"].startswith("INC-")
    assert issue["summary"] == "Test issue"
    assert issue["severity"] == "high"
    assert issue["status"] == "OPEN"


def test_jira_agent_creates_ticket():
    llm = LLMClient()
    mem = ConversationMemory()

    # fresh isolated jira client
    client = JiraClient()
    agent = JiraAgent(llm=llm, memory=mem, client=client)

    resp = agent.handle("Please create a JIRA for high latency between Databricks and Aurora.")

    assert "Mock JIRA ticket created" in resp
    assert "INC-" in resp

    issues = client.list_issues()
    assert len(issues) == 1
    assert "Databricks" in issues[0]["description"]


def test_orchestrator_routes_to_jira_agent():
    orch = Orchestrator()
    resp = orch.route("Please create a JIRA ticket for this incident")

    assert "Mock JIRA ticket created" in resp
    assert "INC-" in resp
