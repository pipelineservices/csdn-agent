import os
from typing import Dict, Any

_RUNBOOK_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "runbooks")


def load_runbook(name: str) -> str:
    path = os.path.join(_RUNBOOK_DIR, name)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_network_context() -> Dict[str, Any]:
    return {
        "network_runbook": load_runbook("network_runbook.md"),
    }


def build_cloudhydra_context() -> Dict[str, Any]:
    return {
        "cloudhydra_runbook": load_runbook("cloudhydra_instructions.md"),
    }
