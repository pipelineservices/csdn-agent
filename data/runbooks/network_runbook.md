# Network Triage Runbook (Sample)

1. Confirm scope: which service, region, and path are impacted.
2. Check recent error and latency metrics in the observability stack.
3. Validate DNS resolution and TLS certificate health.
4. Verify recent config changes (firewall, NACLs, security groups).
5. If only one AZ or region is impacted, consider rerouting traffic.
6. Capture logs and open a JIRA ticket with timeline & hypothesis.
