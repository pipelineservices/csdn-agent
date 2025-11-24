# Cloudhydra connectivity patterns

- Mesh health is sensitive to TLS handshake failures and API 5xx spikes.
- High p99 latency on cloudhydra-api or network-gateway often indicates congestion or misconfiguration.
- Always validate control plane health before deep data-plane debugging.
