# services/cloudhydra_diagnostics_service.py

import json
import os
from typing import Any, Dict, List


_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
_LOG_DIR = os.path.join(_BASE_DIR, "data", "logs")


def _load_json(name: str) -> List[Dict[str, Any]]:
    """
    Load a JSON file from data/logs.
    Returns an empty list if the file doesn't exist or is invalid.
    """
    path = os.path.join(_LOG_DIR, name)
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Ensure we always return a list of dicts
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []
    except Exception:
        return []


def get_cloudhydra_diagnostics(user_query: str) -> Dict[str, Any]:
    """
    Phase-2: central place to assemble a diagnostic snapshot for Cloudhydra.

    For now this is based on local sample JSON files. Later this can call:
    - real AWS APIs (boto3)
    - CSDN Cloudhydra APIs
    - observability providers
    """
    errors = _load_json("sample_errors.json")
    latency = _load_json("sample_latency.json")

    # Very simple derived hints – you can make this smarter later.
    suspected_paths: List[str] = []
    high_latency_regions: List[str] = []

    for item in latency:
        region = item.get("region") or item.get("az") or "unknown"
        p99 = item.get("p99_ms") or item.get("p99") or 0
        if isinstance(p99, (int, float)) and p99 >= 200:
            high_latency_regions.append(region)

    for err in errors:
        path = err.get("path") or err.get("component") or "unknown"
        suspected_paths.append(path)

    return {
        "user_query": user_query,
        "snapshot": {
            "errors": errors,
            "latency": latency,
        },
        "derived_insights": {
            "high_latency_regions": high_latency_regions,
            "suspected_paths": suspected_paths,
        },
        "notes": (
            "This is a Phase-2 synthetic diagnostic snapshot based on local JSON. "
            "In later phases this will be replaced or augmented with live Cloudhydra / AWS data."
        ),
    }
