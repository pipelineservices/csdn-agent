# agent/orchestrator.py

from typing import Literal

from models.shared import LLMClient
from pipeline.memory import ConversationMemory
from pipeline.planner import Planner
from .cloudhydra_agent import CloudhydraAgent
from .triage_agent import TriageAgent
from .jira_agent import JiraAgent


class Orchestrator:
    """
    Phase-2/3 orchestrator:
    - classify intent
    - delegate to TriageAgent, CloudhydraAgent, or JiraAgent
    """

    def __init__(self):
        llm = LLMClient()
        memory = ConversationMemory()

        self.planner = Planner(llm)
        self.triage = TriageAgent(llm, memory)
        self.hydra = CloudhydraAgent(llm, memory)
        self.jira = JiraAgent(llm, memory)

    def route(self, query: str) -> str:
        intent = self.planner.classify_intent(query)

        # Cloudhydra path
        if intent == "cloudhydra":
            return self.hydra.handle(query)

        # JIRA path (intent + simple keyword fallback)
        q_lower = query.lower()
        if intent == "jira" or "jira" in q_lower or "ticket" in q_lower:
            return self.jira.handle(query)

        # Default: network / generic triage
        return self.triage.handle(query)
