---
name: cyber-domain-intelligence
description: "Operational workflow for authorized domain intelligence: correlate DNS, RDAP, TLS, HTTP metadata, reputation, and threat-intelligence evidence into a traceable assessment."
---

# Cyber Domain Intelligence

Apply a deterministic, evidence-first cyber workflow while staying within the user's authorization, the available tools, and the defined scope.

## Activation
- Use when the user asks to investigate, assess, triage, or profile a domain name.
- Use when an incident contains a suspicious domain and the decision depends on infrastructure or reputation evidence.
- Prefer passive and non-invasive collection unless the user has explicitly authorized active testing.

## Operating workflow
1. Normalize the domain and record the exact target, timestamp, scope, and authorization context.
2. Collect DNS records and resolver evidence; note NXDOMAIN, split-horizon, wildcard, CDN, and DNSSEC signals when available.
3. Collect RDAP/registration data and distinguish registrar, registrant privacy, nameservers, registration age, and status codes.
4. Inspect TLS certificate metadata and chain information without treating certificate presence as proof of legitimacy.
5. Collect HTTP response metadata and security-relevant headers using safe requests; avoid state-changing endpoints.
6. Query authorized reputation/threat-intelligence providers when configured and preserve provider-specific timestamps and confidence.
7. Correlate conflicts across sources, identify infrastructure pivots, and separate facts from inference.
8. Return a verdict with confidence, evidence references, limitations, and recommended next steps.

## Preferred tool capabilities
Use these capabilities when they are available through CLEMENT_CYBER_CORE or another authorized provider. Capability names are logical contracts; the orchestrator may map them to concrete MCP/tool names.

- `dns_lookup`
- `rdap_lookup`
- `tls_inspect`
- `http_headers`
- `virustotal_lookup`
- `shodan_lookup`
- `censys_lookup`

## Evidence and provenance rules
- Record the target, tool/provider, retrieval time, and material raw observation for each evidence item.
- Separate verified facts, provider assertions, analyst inference, and recommendations.
- Preserve contradictory evidence instead of silently choosing one source.
- Never convert absence of evidence into evidence of absence.
- Treat reputation, geolocation, ownership, and attribution data as time-sensitive.
- Return `INCONCLUSIVE` when evidence quality is insufficient for a reliable conclusion.

## Safety and authority
- Operate only on assets, data, accounts, files, and infrastructure that are public or that the user is authorized to assess.
- Default to passive, read-only, non-destructive, and minimally invasive collection.
- Require explicit authorization before intrusive, state-changing, destructive, credentialed, broad-scan, or load-generating activity.
- Do not weaken security controls, persist access, conceal activity, or destroy evidence.
- Minimize collection and exposure of personal or secret data.
- Preserve an audit trail for consequential decisions.

## Recommended companion skills
- `$cybersecurity-analyst`
- `$threat-intelligence-analyst`
- `$evidence-seeking-skeptic`
- `$risk-analysis`

## Required output
- **Target and scope**
- **Observed DNS/RDAP/TLS/HTTP facts**
- **Threat-intelligence findings**
- **Correlated indicators**
- **Assessment and confidence**
- **Evidence references and timestamps**
- **Limitations**
- **Next actions**

## Quality gate
- Scope and authorization are explicit enough for the actions performed.
- Evidence is timestamped and traceable to a source/tool.
- Facts and inferences are distinguishable.
- Conflicting or stale evidence is surfaced.
- Confidence is calibrated to evidence quality.
- High-impact next actions are reversible where practical and require human confirmation when consequential.
- The result is usable by the Dynamic Orchestrator and Verifier.

## Invocation arguments
Apply this skill to the current request. Infer only low-risk formatting preferences; ask for missing authorization or scope when it would materially change what actions are allowed.
