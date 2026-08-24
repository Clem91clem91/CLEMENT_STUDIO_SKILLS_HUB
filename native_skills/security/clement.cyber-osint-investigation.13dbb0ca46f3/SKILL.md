---
name: cyber-osint-investigation
description: "Passive cyber-OSINT workflow for authorized investigations, emphasizing source provenance, corroboration, temporal context, privacy minimization, and separation of fact from inference."
---

# Cyber OSINT Investigation

Apply a deterministic, evidence-first cyber workflow while staying within the user's authorization, the available tools, and the defined scope.

## Activation
- Use for passive investigation of cyber infrastructure, public indicators, organizations, campaigns, or incidents.
- Use only public or otherwise authorized information.
- Do not use the workflow to identify, track, or expose private individuals from sensitive personal data.

## Operating workflow
1. Define the research question, scope, lawful/authorized data sources, and stop conditions.
2. Collect public infrastructure and technical evidence from independent sources.
3. Record URLs/source identifiers, timestamps, and retrieval dates for every material claim.
4. Corroborate important facts with at least one independent source where practical.
5. Distinguish direct evidence, provider assertions, analyst inference, and unresolved hypotheses.
6. Minimize personal data and avoid unnecessary deanonymization.
7. Build a timeline and relationship map when it materially improves the investigation.
8. Return findings, confidence, gaps, and next collection priorities.

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
- `$threat-intelligence-analyst`
- `$cybersecurity-analyst`
- `$evidence-seeking-skeptic`
- `$technical-communication`

## Required output
- **Question and scope**
- **Source inventory**
- **Timeline**
- **Correlated technical findings**
- **Hypotheses and confidence**
- **Privacy/attribution caveats**
- **Evidence references**
- **Collection gaps and next actions**

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
