# agent/cloudhydra_agent.py

from models.shared import LLMClient, Message, pretty_json
from pipeline.memory import ConversationMemory
from services.cloudhydra_service import get_cloudhydra_runbook
from services.cloudhydra_diagnostics_service import get_cloudhydra_diagnostics
from . import rag_context


class CloudhydraAgent:
    """
    Phase-2 Cloudhydra agent.

    Responsibilities:
    - Pull Cloudhydra runbook + RAG context
    - Pull a structured diagnostic snapshot (errors, latency, derived hints)
    - Ask the LLM to reason over all of the above
    - Maintain short conversation memory for follow-ups
    """

    def __init__(self, llm: LLMClient | None = None, memory: ConversationMemory | None = None):
        self.llm = llm or LLMClient()
        self.memory = memory or ConversationMemory()

    def handle(self, user_query: str) -> str:
        # 1) Fetch runbook + static context
        runbook = get_cloudhydra_runbook()
        ctx = rag_context.build_cloudhydra_context()

        # 2) Phase-2: fetch diagnostic snapshot
        diag = get_cloudhydra_diagnostics(user_query)

        system_msg = Message(
            role="system",
            content=(
                "You are an expert on the Cloudhydra connectivity platform.\n"
                "You will receive:\n"
                "- The engineer's question\n"
                "- A diagnostic snapshot (errors, latency, derived hints)\n"
                "- Cloudhydra runbook and extra context\n\n"
                "You must:\n"
                "1) Summarize what seems to be happening.\n"
                "2) Propose 1–2 likely root-cause hypotheses.\n"
                "3) Suggest 3–5 concrete next investigation steps.\n"
                "4) If appropriate, suggest mitigations or safe workarounds.\n"
                "Answer in markdown with clear headings and bullet points.\n"
                "Be explicit about any uncertainties or missing data."
            ),
        )

        # Nicely formatted JSON context for the model
        context_block = pretty_json(
            {
                "diagnostics": diag,
                "runbook": runbook,
                "extra_context": ctx,
            }
        )

        user_msg = Message(
            role="user",
            content=(
                f"Engineer question:\n{user_query}\n\n"
                f"=== Cloudhydra Diagnostic Context (JSON) ===\n{context_block}"
            ),
        )

        messages = [system_msg] + self.memory.as_list() + [user_msg]
        answer = self.llm.chat(messages)

        # Update memory for follow-ups
        self.memory.add(Message(role="user", content=user_query))
        self.memory.add(Message(role="assistant", content=answer))

        return answer
