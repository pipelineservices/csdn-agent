from typing import Any, Dict

from models.shared import LLMClient
from pipeline.memory import ConversationMemory
from services.observability_service import get_observability_snapshot
from . import rag_context


class TriageAgent:
    """
    Network SRE triage agent.
    Takes user question + observability snapshot + RAG context
    Returns structured markdown analysis.
    """

    def __init__(self, llm: LLMClient | None = None, memory: ConversationMemory | None = None):
        self.llm = llm or LLMClient()
        self.memory = memory or ConversationMemory()

    def handle(self, user_query: str) -> str:
        # --- 1) Collect data --------------------------------------------------
        observability = get_observability_snapshot()
        runbook = rag_context.build_network_context()

        # --- 2) Construct system directive -----------------------------------
        system_msg = {
            "role": "system",
            "content": (
                "You are a senior network SRE helping triage an incident.\n"
                "You will receive:\n"
                "- User question\n"
                "- Observability snapshot (JSON)\n"
                "- Network runbook\n\n"
                "You must:\n"
                "1) Summarize what seems to be happening.\n"
                "2) Propose a likely root-cause hypothesis.\n"
                "3) Suggest 3 concrete investigation steps.\n"
                "4) Suggest what to capture for a ticket.\n"
                "Answer in clean markdown."
            ),
        }

        # --- 3) User payload --------------------------------------------------
        context_block = {
            "observability": observability,
            "runbook": runbook,
        }

        user_msg = {
            "role": "user",
            "content": (
                f"User question:\n{user_query}\n\n"
                f"Context (JSON):\n{context_block}"
            ),
        }

        # --- 4) Build full conversation context -------------------------------
        full_history = []
        for msg in self.memory.get_history():
            full_history.append(
                {"role": msg["role"], "content": msg["content"]}
            )

        messages = [system_msg] + full_history + [user_msg]

        # --- 5) LLM call -------------------------------------------------------
        answer = self.llm.chat(messages)

        # --- 6) Save memory ----------------------------------------------------
        self.memory.add_user(user_query)
        self.memory.add_assistant(answer)

        return answer
