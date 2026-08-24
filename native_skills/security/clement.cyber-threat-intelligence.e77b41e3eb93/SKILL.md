---
name: cyber-threat-intelligence
description: "Operational threat-intelligence correlation workflow for authorized indicators, combining reputation, exposure, infrastructure, provenance, confidence, and time-sensitive evidence."
---

# Cyber Threat Intelligence

Apply a deterministic, evidence-first cyber workflow while staying within the user's authorization, the available tools, and the defined scope.

## Activation
- Use when the user asks whether an indicator is malicious, suspicious, benign, or related to a known threat.
- Use for domains, IPs, URLs, hashes, or infrastructure indicators.
- Treat third-party detections as evidence signals, not standalone proof.

## Operating workflow
1. Normalize each indicator and record type, source, first-seen context, and collection timestamp.
2. Query configured threat-intelligence providers and preserve raw provider verdicts, dates, and confidence.
3. Correlate infrastructure, reputation, detections, tags, and temporal relationships.
4. Deduplicate repeated provider evidence and avoid multiplying confidence from copied intelligence.
5. Identify stale, contradictory, or low-quality evidence.
6. Map findings to the user's decision context without overclaiming attribution.
7. Produce a confidence-calibrated assessment and clear escalation criteria.

## Preferred tool capabilities
Use these capabilities when they are available through CLEMENT_CYBER_CORE or another authorized provider. Capability names are logical contracts; the orchestrator may map them to concrete MCP/tool names.

- `virustotal_lookup`
- `shodan_lookup`
- `censys_lookup`
- `dns_lookup`
- `rdap_lookup`
- `file_hash_lookup`

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
- `$threat-intelligence-analyst`
- `$cybersecurity-analyst`
- `$adversarial-reasoning`
- `$evidence-seeking-skeptic`

## Required output
- **Indicators**
- **Provider findings**
- **Correlation graph/relationships**
- **Temporal analysis**
- **Assessment and confidence**
- **Evidence provenance**
- **Escalation criteria**
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
