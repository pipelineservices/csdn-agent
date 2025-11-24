from typing import Optional
from models.shared import LLMClient
from pipeline.memory import ConversationMemory
from pipeline.planner import Planner
from .cloudhydra_agent import CloudhydraAgent
from .triage_agent import TriageAgent


class Orchestrator:
    """
    Phase-1 orchestrator:
    - classify intent
    - route to TriageAgent (network/security/jira/smalltalk)
    - route to CloudhydraAgent (cloud)
    """

    def __init__(self):
        self.llm = LLMClient()
        self.memory = ConversationMemory()
        self.planner = Planner()                     # <-- FIX: no param needed
        self.triage = TriageAgent(self.llm, self.memory)
        self.hydra = CloudhydraAgent(self.llm, self.memory)

    def route(self, query: str) -> str:
        intent = self.planner.classify_intent(query)

        # Normalize
        intent = intent.strip().lower()

        # Cloud-related queries go to CloudhydraAgent
        if intent == "cloud":
            return self.hydra.handle(query)

        # Everything else goes through triage
        return self.triage.handle(query)
