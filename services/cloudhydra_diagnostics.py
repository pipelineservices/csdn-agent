# services/cloudhydra_diagnostics.py

"""
Phase-2: Cloudhydra Diagnostic Engine (synthetic version)
---------------------------------------------------------

This module inspects the user's question and generates
a structured diagnostic snapshot:
- errors
- latency
- region hints
- service hints

Later phases can replace the synthetic data with:
- Prometheus / Grafana queries
- CloudWatch metrics
- Cloudhydra control-plane introspection
- Real east-west mesh telemetry
"""

from typing import Dict, Any, List


def _extract_regions(question: str) -> List[str]:
    q = question.lower()
    regions = []
    for r in ["us-east-1", "us-west-2", "onprem-dc1", "onprem-dc2"]:
        if r in q:
            regions.append(r)
    return regions


def _extract_services(question: str) -> List[str]:
    q = question.lower()
    svc = []
    if "databricks" in q:
        svc.append("databricks")
    if "aurora" in q:
        svc.append("aurora-db")
    if "cloudhydra" in q or "mesh" in q:
        svc.append("cloudhydra")
    if "gateway" in q:
        svc.append("network-gateway")
    return svc


def _synthetic_errors(regions: List[str]) -> List[Dict[str, Any]]:
    errors = []

    if "us-east-1" in regions:
        errors.append({
            "component": "cloudhydra-api",
            "region": "us-east-1",
            "error_rate_per_min": 22,
            "recent_5xx": 13,
        })
        errors.append({
            "component": "network-gateway",
            "region": "us-east-1",
            "tls_handshake_failures": 4,
        })

    if "us-west-2" in regions:
        errors.append({
            "component": "cloudhydra-api",
            "region": "us-west-2",
            "error_rate_per_min": 3,
        })

    return errors


def _synthetic_latency(regions: List[str]) -> List[Dict[str, Any]]:
    lat = []

    if "us-east-1" in regions:
        lat.append({
            "component": "cloudhydra-api",
            "region": "us-east-1",
            "latency_ms_p95": 920,
            "latency_ms_p99": 1100,
        })
        lat.append({
            "component": "network-gateway",
            "region": "us-east-1",
            "latency_ms_p95": 480,
            "latency_ms_p99": 685,
        })

    if "us-west-2" in regions:
        lat.append({
            "component": "cloudhydra-api",
            "region": "us-west-2",
            "latency_ms_p95": 210,
            "latency_ms_p99": 340,
        })

    return lat


def get_cloudhydra_diagnostics(question: str) -> Dict[str, Any]:
    """
    MAIN ENTRYPOINT
    ----------------
    Generates a full diagnostic snapshot.
    """

    regions = _extract_regions(question)
    services = _extract_services(question)

    errors = _synthetic_errors(regions)
    latency = _synthetic_latency(regions)

    hints = []

    if "databricks" in services and "aurora-db" in services:
        hints.append("databricks → aurora-db cross-region path may be degraded")

    if "us-east-1" in regions:
        hints.append("observed symptoms concentrate in us-east-1")

    if any("tls" in str(e).lower() for e in errors):
        hints.append("TLS handshake failures may indicate certificate or network issues")

    return {
        "regions_detected": regions,
        "services_detected": services,
        "errors": errors,
        "latency": latency,
        "derived_hints": hints,
    }
