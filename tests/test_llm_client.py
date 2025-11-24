# tests/test_llm_client.py

from models.shared import LLMClient

def test_llm_client_basic():
    llm = LLMClient()
    out = llm.chat([{"role": "user", "content": "Say 'OK' only."}])
    assert "OK" in out.upper()
