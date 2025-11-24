# models/shared.py

from __future__ import annotations

import os
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from openai import OpenAI


# ---------- Data types ----------

@dataclass
class Message:
    role: str
    content: str


# ---------- Small helpers ----------

def pretty_json(obj: Any) -> str:
    """Nice JSON formatting for runbooks / context blocks."""
    return json.dumps(obj, indent=2, default=str)


def load_config() -> Dict[str, Any]:
    """
    Optional project config loader.
    Looks for ../config.json. If missing, returns {}.
    Safe to call from anywhere.
    """
    base_dir = os.path.dirname(__file__)
    cfg_path = os.path.join(base_dir, "..", "config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ---------- LLM client ----------

class LLMClient:
    """
    Single, central wrapper around OpenAI.

    - Reads API key from env: OPENAI_API_KEY
    - Uses chat.completions endpoint
    - Accepts both dict messages and Message objects
    - Always returns plain string
    """

    def __init__(self, model: str = "gpt-4.1-mini", max_tokens: int = 500):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in the environment")

        # Debug once on import / reloader startup
        print(f"DEBUG KEY: {api_key[:10]}")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def chat(self, messages: List[Union[Dict[str, str], Message]]) -> str:
        """
        messages: list of either
          - {"role": "...", "content": "..."} dicts
          - Message(role=..., content=...)
        Returns: assistant message content as str
        """

        # Normalize to OpenAI message dicts
        normalized: List[Dict[str, str]] = []
        for m in messages:
            if isinstance(m, Message):
                normalized.append({"role": m.role, "content": m.content})
            else:
                # assume dict-like
                normalized.append(
                    {
                        "role": m.get("role", "user"),
                        "content": m.get("content", ""),
                    }
                )

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=normalized,
            max_tokens=self.max_tokens,
        )

        # New OpenAI client: .choices[0].message.content is the text
        return resp.choices[0].message.content
