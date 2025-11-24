from agent.orchestrator import Orchestrator


def test_orchestrator_smoke():
    orch = Orchestrator()
    # we don't hit the real LLM in CI normally, but for local smoke:
    # comment this out if you don't have OPENAI_API_KEY set
    assert hasattr(orch, "route")
