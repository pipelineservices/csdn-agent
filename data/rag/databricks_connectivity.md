# Databricks ↔ Aurora connectivity

- Prefer same-region connectivity to avoid cross-region latency.
- If crossing regions, confirm DNS resolves to the right Aurora writer/reader endpoints.
- Validate security groups allow Databricks subnets to reach Aurora on the correct port.
