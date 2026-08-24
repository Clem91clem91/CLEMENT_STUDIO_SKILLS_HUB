---
name: cyber-file-triage
description: "Non-executing file triage workflow for authorized files: compute hashes, inspect metadata, identify type/signature inconsistencies, and correlate reputation evidence without running untrusted content."
---

# Cyber File Triage

Apply a deterministic, evidence-first cyber workflow while staying within the user's authorization, the available tools, and the defined scope.

## Activation
- Use when the user asks whether a file is suspicious or needs initial malware triage.
- Use when a file can be inspected safely without executing it.
- Do not execute, detonate, enable macros, or open active content unless a dedicated isolated sandbox is explicitly authorized and available.

## Operating workflow
1. Record file provenance, acquisition time, expected type, and authorization context.
2. Compute cryptographic hashes without modifying the file.
3. Inspect file type, magic/signature, size, extension consistency, and available static metadata.
4. Extract safe metadata and obvious static indicators without executing embedded code.
5. Query configured reputation services by hash when permitted.
6. Correlate metadata anomalies, reputation, signing information, and provenance.
7. Classify the triage result as benign-leaning, suspicious, malicious-evidence-present, or inconclusive with confidence.
8. Preserve chain-of-custody notes and recommend isolation/escalation when needed.

## Preferred tool capabilities
Use these capabilities when they are available through CLEMENT_CYBER_CORE or another authorized provider. Capability names are logical contracts; the orchestrator may map them to concrete MCP/tool names.

- `file_hash`
- `file_metadata`
- `file_type_inspect`
- `virustotal_lookup`

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
- `$incident-responder`
- `$evidence-seeking-skeptic`
- `$risk-analysis`

## Required output
- **File identity and hashes**
- **Static metadata**
- **Reputation findings**
- **Observed anomalies**
- **Triage assessment and confidence**
- **Chain-of-custody/evidence refs**
- **Recommended containment or next analysis**

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
