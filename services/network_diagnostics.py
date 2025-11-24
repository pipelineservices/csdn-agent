# services/network_diagnostics.py

"""
Phase-2: Advanced Network Diagnostics for TriageAgent
-----------------------------------------------------

This module generates:
- latency samples per region
- packet loss estimates
- error spikes
- cross-region path analysis
- diagnostic hints
"""

from typing import Dict, Any, List


def _extract_regions(question: str) -> List[str]:
    q = question.lower()
    regions = []
    for r in ["us-east-1", "us-west-2", "onprem-dc1", "onprem-dc2"]:
        if r in q:
            regions.append(r)
    return regions


def _generate_latency(regions: List[str]) -> List[Dict[str, Any]]:
    lat = []

    if "us-east-1" in regions:
        lat.append({
            "region": "us-east-1",
            "p95_ms": 320,
            "p99_ms": 460,
        })

    if "us-west-2" in regions:
        lat.append({
            "region": "us-west-2",
            "p95_ms": 190,
            "p99_ms": 260,
        })

    if "onprem-dc1" in regions:
        lat.append({
            "region": "onprem-dc1",
            "p95_ms": 540,
            "p99_ms": 810,
        })

    return lat


def _generate_packet_loss(regions: List[str]) -> List[Dict[str, Any]]:
    loss = []

    if "us-east-1" in regions:
        loss.append({"region": "us-east-1", "loss_pct": 1.8})

    if "onprem-dc1" in regions:
        loss.append({"region": "onprem-dc1", "loss_pct": 3.1})

    return loss


def _generate_errors(regions: List[str]) -> List[Dict[str, Any]]:
    errors = []

    if "us-east-1" in regions:
        errors.append({
            "component": "csdn-edge-router",
            "region": "us-east-1",
            "error_rate_per_min": 14,
        })

    if "onprem-dc1" in regions:
        errors.append({
            "component": "onprem-firewall",
            "region": "onprem-dc1",
            "error_rate_per_min": 6,
        })

    return errors


def _generate_hints(lat: List[Dict[str, Any]], loss: List[Dict[str, Any]]) -> List[str]:
    hints = []

    for entry in lat:
        if entry["p99_ms"] > 600:
            hints.append(f"High p99 latency in {entry['region']} suggests congestion or routing degradation.")

    for entry in loss:
        if entry["loss_pct"] > 2.0:
            hints.append(f"Packet loss in {entry['region']} exceeds healthy threshold.")

    return hints


def get_network_diagnostics(question: str) -> Dict[str, Any]:
    regions = _extract_regions(question)

    lat = _generate_latency(regions)
    loss = _generate_packet_loss(regions)
    errors = _generate_errors(regions)
    hints = _generate_hints(lat, loss)

    return {
        "regions_detected": regions,
        "latency": lat,
        "packet_loss": loss,
        "errors": errors,
        "derived_hints": hints,
    }
