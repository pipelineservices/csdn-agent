from typing import Dict, Any, List

from .network_state_service import get_recent_errors, get_latency_samples


def get_observability_snapshot() -> Dict[str, List[Dict[str, Any]]]:
    """
    Phase-1: just wraps sample JSON.
    In later phases this becomes real queries to your observability stack.
    """
    return {
        "errors": get_recent_errors(),
        "latency": get_latency_samples(),
    }
