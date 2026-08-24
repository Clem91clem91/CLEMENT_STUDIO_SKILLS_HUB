# CLEMENT Native Cyber Skills Extension

This extension adds eight operational cybersecurity skills without rewriting the
certified 905-skill import snapshot.

## Why an overlay

`registry/skills_registry.json` is evidence of the audited source libraries and
is validated against the P0 audit contract. Editing its counts to include
hand-authored skills would make the audit metrics misleading.

The runtime model is therefore:

1. load `registry/skills_registry.json` (certified imported corpus);
2. load `registry/native_skills_registry.json` (CLEMENT-native skills);
3. apply `registry/category_overrides.json` (non-destructive metadata fixes);
4. use `clement_skills_hub.extensions.effective_skill_entries()` as the
   effective view for downstream consumers.

No merge, tag, release, or certification is implied by the presence of this
extension. Native skills remain `CANDIDATE` until CI and real Skills MCP /
Odysseus tests pass.

## Added operational skills

- `cyber-domain-intelligence`
- `cyber-ip-intelligence`
- `cyber-web-security-audit`
- `cyber-threat-intelligence`
- `cyber-file-triage`
- `cyber-osint-investigation`
- `cyber-network-diagnostics`
- `cyber-incident-triage`

All eight are evidence-first, authorization-aware, passive-by-default workflows
intended to orchestrate CLEMENT_CYBER_CORE capabilities rather than duplicate
individual tool implementations.

## Metadata corrections

The effective view reclassifies these existing role skills as `security`
without altering their certified source manifests:

- `cybersecurity-analyst`
- `incident-responder`
- `network-engineer`
- `penetration-tester`

## Downstream integration

CLEMENT Skills MCP should consume the effective view instead of reading only
the certified base registry. That adapter change is intentionally separate from
this Skills Hub update so the Hub and MCP can be validated independently.
