# agent/orchestrator.py

from __future__ import annotations

from typing import Dict

from models.shared import LLMClient
from pipeline.memory import ConversationMemory
from pipeline.planner import Planner
from agent.triage_agent import TriageAgent
from agent.cloudhydra_agent import CloudhydraAgent


class Orchestrator:
    """
    Top-level router for the SRE copilot.

    Phase-2:
    - Can route to network triage agent
    - Can route to Cloudhydra agent
    - Can optionally call BOTH and fuse their answers (multi-agent mode)
    - Provides simple JIRA + chitchat handling
    """

    def __init__(
        self,
        llm: LLMClient | None = None,
        memory: ConversationMemory | None = None,
    ) -> None:
        self.llm = llm or LLMClient()
        self.memory = memory or ConversationMemory()

        # Reuse the same llm + memory for child agents so the convo is coherent.
        self.triage_agent = TriageAgent(self.llm, self.memory)
        self.cloudhydra_agent = CloudhydraAgent(self.llm, self.memory)

        self.planner = Planner(self.llm)

    # ------------------------------------------------------------------ #
    # Multi-agent fusion helper
    # ------------------------------------------------------------------ #
    def _fuse_multi_agent(self, query: str, partial: Dict[str, str]) -> str:
        """
        Combine reports from multiple specialist agents into a single answer.

        `partial` maps agent name -> markdown output.
        """
        system_msg = {
            "role": "system",
            "content": (
                "You are a senior SRE combining reports from multiple specialist agents "
                "into a single concise triage response.\n\n"
                "You will be given:\n"
                "- The original engineer question\n"
                "- One or more agent reports (network, cloudhydra, etc.)\n\n"
                "Your job:\n"
                "1) Produce ONE unified markdown answer for the on-call engineer.\n"
                "2) Merge and de-duplicate content from the reports.\n"
                "3) Keep structure clear: summary, hypotheses, next steps, and ticket notes.\n"
                "4) If agents disagree, call it out and explain briefly.\n"
                "Do NOT mention that there were multiple agents; just sound like one expert."
            ),
        }

        blocks = []
        for name, text in partial.items():
            pretty_name = name.capitalize()
            blocks.append(f"=== {pretty_name} agent report ===\n{text}\n")

        user_msg = {
            "role": "user",
            "content": (
                f"Original question:\n{query}\n\n"
                + "\n".join(blocks)
                + "\nProduce a single unified triage answer in markdown."
            ),
        }

        return self.llm.chat([system_msg, user_msg])

    # ------------------------------------------------------------------ #
    # Main routing function
    # ------------------------------------------------------------------ #
    def route(self, query: str) -> str:
        """
        Decide which agents to call for this query, and optionally fuse responses.
        """
        intents = self.planner.classify_intents(query)

        # ---- Multi-agent: network + Cloudhydra --------------------------- #
        if "network" in intents and "cloudhydra" in intents:
            partial: Dict[str, str] = {}
            partial["network"] = self.triage_agent.handle(query)
            partial["cloudhydra"] = self.cloudhydra_agent.handle(query)
            return self._fuse_multi_agent(query, partial)

        # ---- Single primary intent path (backwards compatible) ----------- #
        primary = intents[0]

        # Network triage only
        if primary == "network":
            return self.triage_agent.handle(query)

        # Cloudhydra only
        if primary == "cloudhydra":
            return self.cloudhydra_agent.handle(query)

        # JIRA (Phase-3 placeholder)
        if primary == "jira":
            return (
                "This looks like a JIRA / ticket workflow.\n\n"
                "Phase-2 does not yet call JIRA APIs. "
                "For now, please create or update the ticket in your JIRA instance manually, "
                "using the investigation guidance from the network / Cloudhydra agents."
            )

        # Chitchat / small talk
        if primary == "chitchat":
            return self.llm.chat(
                [
                    {
                        "role": "system",
                        "content": (
                            "You are a friendly but concise assistant. "
                            "Keep replies short and casual."
                        ),
                    },
                    {"role": "user", "content": query},
                ]
            )

        # Fallback – treat as network incident
        return self.triage_agent.handle(query)
