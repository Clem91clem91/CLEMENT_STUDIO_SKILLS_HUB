---
name: cyber-incident-triage
description: "Operational incident-triage workflow that combines file, domain, IP, web, and threat-intelligence evidence to prioritize containment, investigation, and escalation without destroying evidence."
---

# Cyber Incident Triage

Apply a deterministic, evidence-first cyber workflow while staying within the user's authorization, the available tools, and the defined scope.

## Activation
- Use when the user reports a suspected cyber incident or needs initial prioritization of technical indicators.
- Use to organize evidence and determine urgency, containment needs, and next investigative steps.
- Do not perform destructive remediation or evidence-altering actions without explicit approval.

## Operating workflow
1. Record incident owner, time detected, affected assets, business impact, authorization, and immediate safety constraints.
2. Preserve evidence and identify volatile data that may be lost.
3. Normalize and classify available indicators: domains, IPs, URLs, files/hashes, users, endpoints, and timestamps.
4. Invoke the relevant domain/IP/file/web/threat-intelligence workflows for each indicator type.
5. Build a timeline and correlate evidence across sources.
6. Estimate severity, scope, confidence, and whether active compromise is indicated.
7. Recommend reversible containment first; distinguish containment, eradication, recovery, and monitoring.
8. Define escalation triggers and handoff artifacts for an accountable human responder.

## Preferred tool capabilities
Use these capabilities when they are available through CLEMENT_CYBER_CORE or another authorized provider. Capability names are logical contracts; the orchestrator may map them to concrete MCP/tool names.

- `dns_lookup`
- `rdap_lookup`
- `tls_inspect`
- `http_headers`
- `virustotal_lookup`
- `shodan_lookup`
- `censys_lookup`
- `file_hash`
- `file_metadata`

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
- `$incident-responder`
- `$cybersecurity-analyst`
- `$threat-intelligence-analyst`
- `$crisis-communication`
- `$risk-analysis`

## Required output
- **Incident summary**
- **Affected assets and indicators**
- **Timeline**
- **Correlated evidence**
- **Severity and confidence**
- **Containment priorities**
- **Preservation requirements**
- **Escalation and next actions**

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
