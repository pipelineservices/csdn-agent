# agent/cloudhydra_agent.py

from models.shared import LLMClient, Message, pretty_json
from pipeline.memory import ConversationMemory
from services.cloudhydra_service import get_cloudhydra_runbook
from services.cloudhydra_diagnostics import get_cloudhydra_diagnostics
from pipeline.correlation import correlate_cloudhydra
from pipeline.rag_engine import search_rag
from . import rag_context


class CloudhydraAgent:
    """
    Cloudhydra SRE agent (Phase-2 + RAG):
    - Uses diagnostics
    - Uses correlation engine
    - Uses RAG over Cloudhydra / connectivity docs
    """

    def __init__(self, llm: LLMClient | None = None, memory: ConversationMemory | None = None):
        self.llm = llm or LLMClient()
        self.memory = memory or ConversationMemory()

    def handle(self, user_query: str) -> str:
        # 1) Gather inputs
        runbook = get_cloudhydra_runbook()
        ctx = rag_context.build_cloudhydra_context()
        diag = get_cloudhydra_diagnostics(user_query)

        # Make sure observability is a dict before giving to correlation
        observability = {}
        if isinstance(diag, dict) and isinstance(diag.get("observability"), dict):
            observability = diag.get("observability", {})

        # 2) Apply correlation (safe, even if diag/obs are sparse)
        correlation = correlate_cloudhydra(diag if isinstance(diag, dict) else {}, observability)

        # 3) RAG over Cloudhydra connectivity docs
        rag_hits = search_rag(user_query, domain="cloudhydra", top_k=3)

        # 4) Build JSON context block for the LLM
        context_block = pretty_json(
            {
                "diagnostics": diag,
                "correlation": correlation,
                "rag_hits": rag_hits,
                "runbook": runbook,
                "extra_context": ctx,
            }
        )

        # 5) System instruction
        system_msg = Message(
            role="system",
            content=(
                "You are an expert on the Cloudhydra connectivity platform.\n"
                "You will receive:\n"
                "- The engineer's question\n"
                "- A diagnostic snapshot (errors, latency, derived hints)\n"
                "- Correlation summary\n"
                "- RAG hits from Cloudhydra-related knowledge\n"
                "- Cloudhydra runbook and extra context\n\n"
                "You must:\n"
                "1) Summarize what seems to be happening.\n"
                "2) Propose 1–2 likely root-cause hypotheses.\n"
                "3) Suggest 3–5 concrete next investigation steps.\n"
                "4) If appropriate, suggest mitigations or safe workarounds.\n"
                "Be explicit about any uncertainties or missing data.\n"
                "Answer in markdown with clear headings and bullet points."
            ),
        )

        # 6) User message
        user_msg = Message(
            role="user",
            content=(
                f"Engineer question:\n{user_query}\n\n"
                f"=== Cloudhydra Context (JSON) ===\n{context_block}"
            ),
        )

        # 7) Conversation history + LLM call
        messages = [system_msg] + self.memory.as_list() + [user_msg]
        answer = self.llm.chat(messages)

        # 8) Update memory
        self.memory.add_user(user_query)
        self.memory.add_assistant(answer)

        return answer
