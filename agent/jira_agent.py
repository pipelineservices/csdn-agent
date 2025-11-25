# agent/jira_agent.py

from __future__ import annotations
from typing import Optional

from models.shared import LLMClient
from pipeline.memory import ConversationMemory
from services.jira_client import JiraClient, jira_client


class JiraAgent:
    """
    Mock JIRA agent (Option C).

    - No real JIRA API calls
    - Uses JiraClient in-memory store
    - Creates simple incident tickets from free-form user text
    """

    def __init__(
        self,
        llm: Optional[LLMClient] = None,
        memory: Optional[ConversationMemory] = None,
        client: Optional[JiraClient] = None,
    ) -> None:
        self.llm = llm or LLMClient()
        self.memory = memory or ConversationMemory()
        self.client = client or jira_client

    def handle(self, user_query: str) -> str:
        """
        For now, always interprets the request as:
        'create an incident ticket from this text'.
        """

        summary = self._summarize_summary(user_query)
        description = self._build_description(user_query)

        issue = self.client.create_issue(
            summary=summary,
            description=description,
            severity="medium",
        )

        # store a tiny trace in memory
        self.memory.add_user(user_query)
        self.memory.add_assistant(f"Created mock JIRA {issue['key']}")

        return (
            "Mock JIRA ticket created:\n"
            f"- Key: {issue['key']}\n"
            f"- Summary: {issue['summary']}\n"
            f"- Status: {issue['status']}\n"
        )

    # -------- helpers (deterministic, no extra LLM parsing) ----------

    def _summarize_summary(self, user_query: str) -> str:
        text = user_query.strip().replace("\n", " ")
        return text[:80] if len(text) > 80 else text

    def _build_description(self, user_query: str) -> str:
        return user_query.strip()
