import os

_RUNBOOK_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "runbooks")


def get_cloudhydra_runbook() -> str:
    path = os.path.join(_RUNBOOK_DIR, "cloudhydra_instructions.md")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
