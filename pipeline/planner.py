# pipeline/planner.py

from __future__ import annotations

from typing import List
from models.shared import LLMClient


class Planner:
    """
    Lightweight router that decides which specialist agents to call.

    Agents:
    - network     : Network / Databricks / Aurora / latency incidents
    - cloudhydra  : Cloudhydra mesh / connectivity platform
    - jira        : Ticketing / JIRA workflows
    - chitchat    : Greetings, small talk
    """

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    # ---- NEW: multi-intent classifier ------------------------------------- #
    def classify_intents(self, query: str) -> List[str]:
        """
        Return one or more agent labels (network, cloudhydra, jira, chitchat).

        The LLM is asked to return a comma-separated list, all lower-case,
        with no extra text. We then normalise and validate.
        """
        system_msg = {
            "role": "system",
            "content": (
                "You are a router for an SRE copilot. "
                "Given a user query, decide which specialist agents should answer.\n\n"
                "Valid agent names:\n"
                "- network   : network incidents, Databricks ↔ Aurora, latency, packet loss\n"
                "- cloudhydra: Cloudhydra mesh / connectivity platform\n"
                "- jira      : JIRA / ticket operations (create / update / comment)\n"
                "- chitchat  : greetings or casual conversation\n\n"
                "Rules:\n"
                "- Return one or more agent names.\n"
                "- Output ONLY a comma-separated list of names, all lower-case.\n"
                "- No explanations, no extra words."
            ),
        }
        user_msg = {
            "role": "user",
            "content": f"Query: {query}",
        }

        raw = self.llm.chat([system_msg, user_msg]).strip().lower()

        # Normalise into tokens
        # e.g. "network, cloudhydra" or "network and jira"
        raw = raw.replace("and", ",")
        tokens = [t.strip() for t in raw.split(",") if t.strip()]

        allowed = {"network", "cloudhydra", "jira", "chitchat"}
        intents: List[str] = [t for t in tokens if t in allowed]

        # Fallback heuristics if LLM response is off-format
        if not intents:
            q = query.lower()
            if "jira" in q or "ticket" in q:
                intents = ["jira"]
            elif "cloudhydra" in q or "mesh" in q:
                intents = ["cloudhydra"]
            elif any(x in q for x in ["hello", "hi ", "hi,", "hey"]):
                intents = ["chitchat"]
            else:
                intents = ["network"]

        # Remove duplicates while preserving order
        deduped: List[str] = list(dict.fromkeys(intents))
        return deduped

    # ---- Backwards-compatible single intent ------------------------------- #
    def classify_intent(self, query: str) -> str:
        """
        Kept for backwards compatibility. Returns the primary intent only.
        """
        return self.classify_intents(query)[0]
