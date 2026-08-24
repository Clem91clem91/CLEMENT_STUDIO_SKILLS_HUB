---
name: cyber-network-diagnostics
description: "Authorized network-diagnostics workflow for troubleshooting connectivity and defensive posture using minimally invasive observations, explicit scope, and evidence-preserving checks."
---

# Cyber Network Diagnostics

Apply a deterministic, evidence-first cyber workflow while staying within the user's authorization, the available tools, and the defined scope.

## Activation
- Use when the user needs to diagnose a network, host, route, DNS path, or service they own or are authorized to assess.
- Default to local, passive, or low-impact diagnostics.
- Require explicit authorization before broad scanning, intrusive enumeration, credentialed testing, disruption, or evasion.

## Operating workflow
1. Define the approved network scope, affected service, expected behavior, and change constraints.
2. Collect local interface, route, DNS, and reachability observations where authorized.
3. Test only the minimum endpoints/ports necessary to answer the troubleshooting question.
4. Differentiate name-resolution, routing, firewall, transport, TLS, application, and upstream-provider failure modes.
5. Capture commands/tool calls, timestamps, and observed results.
6. Avoid configuration changes unless separately approved.
7. Identify likely root cause, confidence, and the smallest reversible next action.

## Preferred tool capabilities
Use these capabilities when they are available through CLEMENT_CYBER_CORE or another authorized provider. Capability names are logical contracts; the orchestrator may map them to concrete MCP/tool names.

- `network_interfaces`
- `route_inspect`
- `dns_lookup`
- `reachability_check`
- `tcp_connect_test`
- `tls_inspect`

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
- `$network-engineer`
- `$security-engineer`
- `$root-cause-reasoning`
- `$incident-responder`

## Required output
- **Scope**
- **Observed network state**
- **Layer-by-layer diagnostics**
- **Likely root cause**
- **Confidence and alternatives**
- **Evidence references**
- **Minimal next action**

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
