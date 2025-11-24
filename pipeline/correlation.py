# pipeline/correlation.py

"""
Correlation Engine (Phase-2D)

Takes diagnostics + observability + runbook context
Returns correlation insights that can be merged into an agent's answer.

This engine does NOT call LLM — it is deterministic and rule-based.
"""

from typing import Dict, Any, List


def correlate_network(diagnostics: Dict[str, Any], observability: Dict[str, Any]) -> Dict[str, Any]:
    """
    Basic rule-based correlation for network triage.
    """

    issues = []
    score = 0

    # --- Latency correlation -------------------------------------------------
    if diagnostics.get("latency_ms", 0) > 120:
        issues.append("High latency detected (>120 ms).")
        score += 2

    if observability.get("p95_latency_ms", 0) > 150:
        issues.append("Observability shows elevated p95 latency.")
        score += 2

    # --- Packet loss ---------------------------------------------------------
    if diagnostics.get("packet_loss_percent", 0) > 1:
        issues.append("Packet loss detected (>1%).")
        score += 3

    # --- Error codes ---------------------------------------------------------
    if observability.get("errors_last_5m", 0) > 20:
        issues.append("Spike in error rate.")
        score += 2

    # --- Derived probable cause ---------------------------------------------
    if score >= 5:
        probable = "Network congestion or misconfigured routing."
    elif score >= 3:
        probable = "Intermittent regional network degradation."
    elif score >= 1:
        probable = "Minor latency rises; needs verification."
    else:
        probable = "No strong signals; likely transient."

    return {
        "detected_issues": issues,
        "score": score,
        "probable_cause": probable,
    }


def correlate_cloudhydra(diag: Dict[str, Any], observability: Dict[str, Any]) -> Dict[str, Any]:
    """
    Correlation for Cloudhydra mesh health.
    """

    issues = []
    score = 0

    if diag.get("api_error_rate", 0) > 5:
        issues.append("Cloudhydra API errors elevated.")
        score += 3

    if diag.get("tls_failures", 0) > 2:
        issues.append("TLS handshake failures detected.")
        score += 3

    if observability.get("p99_latency_ms", 0) > 800:
        issues.append("High p99 latency at Cloudhydra gateway.")
        score += 2

    if score >= 6:
        probable = "Control plane or TLS failures in Cloudhydra."
    elif score >= 3:
        probable = "Possible gateway saturation or cert issues."
    else:
        probable = "No strong Cloudhydra indicators."

    return {
        "detected_issues": issues,
        "score": score,
        "probable_cause": probable,
    }
