# services/network_state_service.py

from typing import Any, Dict, List


def get_recent_errors() -> List[Dict[str, Any]]:
    """
    Phase-1 mock data.
    Later we can wire this to real logs / metrics APIs.
    """
    return [
        {
            "timestamp": "2025-01-10T12:00:00Z",
            "service": "cloudhydra-gateway",
            "severity": "ERROR",
            "message": "Packet drop detected between CSDN and AWS TGW",
        },
        {
            "timestamp": "2025-01-10T12:05:00Z",
            "service": "csdn-edge-router",
            "severity": "WARN",
            "message": "Latency spike above 200ms on east-west path",
        },
    ]


def get_latency_samples() -> List[Dict[str, Any]]:
    """
    Phase-1 mock latency samples.
    """
    return [
        {"region": "us-east-1", "p95_ms": 120, "p99_ms": 180},
        {"region": "us-west-2", "p95_ms": 95, "p99_ms": 140},
        {"region": "onprem-dc1", "p95_ms": 160, "p99_ms": 230},
    ]
