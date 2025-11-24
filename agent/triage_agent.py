# agent/triage_agent.py

from models.shared import LLMClient, pretty_json
from pipeline.memory import ConversationMemory
from services.observability_service import get_observability_snapshot
from pipeline.rag_engine import search_rag
from . import rag_context


class TriageAgent:
    """
    Network SRE triage agent (Phase-2 + RAG).
    Uses:
      - Observability snapshot
      - Network runbook
      - RAG over network / TGW / connectivity docs
    """

    def __init__(self, llm: LLMClient | None = None, memory: ConversationMemory | None = None):
        self.llm = llm or LLMClient()
        self.memory = memory or ConversationMemory()

    def handle(self, user_query: str) -> str:
        # 1) Collect data
        observability = get_observability_snapshot()
        runbook_ctx = rag_context.build_network_context()

        # 2) RAG hits for network domain
        rag_hits = search_rag(user_query, domain="network", top_k=3)

        # 3) System directive
        system_msg = {
            "role": "system",
            "content": (
                "You are a senior network SRE helping triage an incident.\n"
                "You will receive:\n"
                "- User question\n"
                "- Observability snapshot (JSON)\n"
                "- Network runbook\n"
                "- RAG hits from network troubleshooting knowledge\n\n"
                "You must:\n"
                "1) Summarize what seems to be happening.\n"
                "2) Propose a likely root-cause hypothesis.\n"
                "3) Suggest 3 concrete investigation steps.\n"
                "4) Suggest what to capture for a ticket.\n"
                "Answer in clean markdown."
            ),
        }

        # 4) Build context block
        context_block = pretty_json(
            {
                "observability": observability,
                "runbook": runbook_ctx,
                "rag_hits": rag_hits,
            }
        )

        user_msg = {
            "role": "user",
            "content": (
                f"User question:\n{user_query}\n\n"
                f"=== Network Context (JSON) ===\n{context_block}"
            ),
        }

        # 5) Full conversation history
        history = self.memory.as_list()
        messages = [system_msg] + history + [user_msg]

        # 6) LLM call
        answer = self.llm.chat(messages)

        # 7) Save memory
        self.memory.add_user(user_query)
        self.memory.add_assistant(answer)

        return answer
