---
name: cyber-web-security-audit
description: "Safe, evidence-driven audit workflow for web-facing security posture using TLS and HTTP metadata, security headers, redirects, and non-destructive observations."
---

# Cyber Web Security Audit

Apply a deterministic, evidence-first cyber workflow while staying within the user's authorization, the available tools, and the defined scope.

## Activation
- Use when the user asks for a security review of a website or web endpoint they own or are authorized to assess.
- Use for passive posture checks that do not exploit vulnerabilities or alter server state.
- Require explicit authorization before any active, intrusive, destructive, authenticated, or load-generating testing.

## Operating workflow
1. Record the exact URL/host, scope, authorization, environment, and test constraints.
2. Inspect TLS protocol/certificate metadata and flag expiry, hostname, trust-chain, or weak-configuration signals when observable.
3. Collect HTTP status, redirect chain, server metadata, and security-relevant headers.
4. Assess common defensive headers such as HSTS, CSP, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, and framing controls where applicable.
5. Identify information leakage from headers or banners without attempting exploitation.
6. Separate confirmed misconfiguration from best-practice recommendations.
7. Assign severity based on exploitability evidence, business context, and uncertainty.
8. Return remediation priorities and reproducible evidence.

## Preferred tool capabilities
Use these capabilities when they are available through CLEMENT_CYBER_CORE or another authorized provider. Capability names are logical contracts; the orchestrator may map them to concrete MCP/tool names.

- `tls_inspect`
- `http_headers`
- `http_redirect_chain`
- `security_headers_analyze`

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
- `$security-engineer`
- `$cybersecurity-analyst`
- `$risk-analysis`
- `$standards-driven-professional`

## Required output
- **Scope and authorization**
- **Observed TLS posture**
- **Observed HTTP/security headers**
- **Findings with severity**
- **Evidence references**
- **False-positive/uncertainty notes**
- **Prioritized remediation**

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
