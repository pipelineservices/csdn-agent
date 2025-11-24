# pipeline/memory.py
from typing import List, Dict, Any
from models.shared import Message


class ConversationMemory:
    """Simple in-memory history with Message objects."""

    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self.history: List[Message] = []

    # Phase-2 API ------------------------------

    def add(self, msg: Message):
        """Store a Message object."""
        self.history.append(msg)
        # keep memory small
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages:]

    def as_list(self) -> List[Message]:
        """Return last N messages as list of Message objects."""
        return self.history[-self.max_messages:]

    # Backwards compatibility (Phase-1 APIs) ----

    def add_user(self, text: str):
        self.add(Message(role="user", content=text))

    def add_assistant(self, text: str):
        self.add(Message(role="assistant", content=text))

    def get_history(self) -> List[Dict[str, Any]]:
        """Return history as list of dicts (Phase-1 compatibility)."""
        return [{"role": m.role, "content": m.content} for m in self.as_list()]
