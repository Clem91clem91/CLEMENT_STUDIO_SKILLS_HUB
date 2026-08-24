---
name: cyber-ip-intelligence
description: "Operational workflow for authorized IP intelligence: correlate reverse DNS, RDAP/ASN, network ownership, exposure, geolocation hints, and threat-intelligence evidence."
---

# Cyber IP Intelligence

Apply a deterministic, evidence-first cyber workflow while staying within the user's authorization, the available tools, and the defined scope.

## Activation
- Use when the user asks to investigate or triage an IPv4 or IPv6 address.
- Use when an incident contains a suspicious remote address and infrastructure attribution matters.
- Do not infer a person's identity from IP data; treat geolocation as approximate infrastructure metadata.

## Operating workflow
1. Validate and normalize the IP address and record scope, timestamp, and authorization context.
2. Collect reverse DNS and RDAP/ASN ownership information.
3. Collect coarse geolocation or hosting-provider hints only from authorized sources and label their uncertainty.
4. Query configured threat-intelligence/exposure providers such as VirusTotal, Shodan, or Censys.
5. Correlate ports/services only from authorized passive or previously observed data unless active probing is explicitly authorized.
6. Identify shared-hosting, CDN, cloud, VPN, NAT, or anycast conditions that weaken attribution.
7. Return a confidence-calibrated infrastructure assessment with evidence references.

## Preferred tool capabilities
Use these capabilities when they are available through CLEMENT_CYBER_CORE or another authorized provider. Capability names are logical contracts; the orchestrator may map them to concrete MCP/tool names.

- `reverse_dns_lookup`
- `ip_rdap_lookup`
- `ip_geolocation_lookup`
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
- `$network-engineer`
- `$evidence-seeking-skeptic`

## Required output
- **Target and scope**
- **Ownership/ASN facts**
- **Reverse DNS and hosting signals**
- **Exposure/threat-intelligence findings**
- **Attribution caveats**
- **Assessment and confidence**
- **Evidence references**
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
