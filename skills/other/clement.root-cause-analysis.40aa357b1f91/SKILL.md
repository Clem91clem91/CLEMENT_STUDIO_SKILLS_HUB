---
name: root-cause-analysis
description: "Performs root cause analysis through traceable evidence, appropriate methods, robustness checks, calibrated findings, and decision-ready recommendations. Use for tasks explicitly involving Root Cause Analysis."
---

# Root Cause Analysis

Produce a traceable analysis from defined questions, suitable evidence, appropriate methods, and calibrated conclusions.

## Activation
- Use when the user explicitly asks for root cause analysis.
- Use when a task would materially benefit from the methods, standards, or operating style associated with root cause analysis.
- Use when evidence must be transformed into traceable findings, comparisons, diagnosis, forecasting, or recommendations.

## Operating instructions
1. Define the analysis question, decision context, scope, unit of analysis, time horizon, and success criteria.
2. Inventory sources, data definitions, provenance, recency, completeness, permissions, and likely biases.
3. Clean, normalize, reconcile, and document the evidence before drawing conclusions.
4. Select methods appropriate to the data and question; state assumptions and limitations.
5. Perform the analysis with reproducible calculations, comparisons, and intermediate checks.
6. Test robustness using sensitivity analysis, alternative explanations, edge cases, and data-quality challenges.
7. Separate observations, interpretations, implications, recommendations, and confidence levels.
8. Deliver an executive summary, methodology, findings, evidence, limitations, and next analyses.

## Skill-specific focus
- Primary capability: Root Cause Analysis.
- Primary domain: data analytics.
- Apply root cause analysis as an explicit repeatable protocol.
- Produce an artifact that another agent or human can review and reuse.
- State assumptions, uncertainties, and completion criteria.

## Required output
- **Executive Summary**: Concise answer or decision-ready overview.
- **Objective And Scope**: Restated objective, scope, constraints, and acceptance criteria.
- **Inputs And Assumptions**: Evidence used, missing inputs, assumptions, and source dates.
- **Work Product**: Methodology, data-quality findings, calculations, results, robustness checks, and interpretation.
- **Risks And Limitations**: Material risks, uncertainty, limitations, and review triggers.
- **Quality Checks**: Validation performed and unresolved checks.
- **Next Actions**: Prioritized actions with suggested owners and timing.

## Quality gate
- The objective, scope, audience, constraints, and definition of done are explicit.
- Facts, calculations, assumptions, interpretations, recommendations, and uncertainty are distinguishable.
- Sources and inputs are traceable, current enough, authorized, and appropriate to the stakes.
- The deliverable is internally consistent and directly usable by its intended audience.
- Material risks, limitations, dependencies, and human review triggers are visible.
- The next actions are prioritized and include ownership or a clear decision request.
- Quality criterion checked: method fit.
- Quality criterion checked: data quality.
- Quality criterion checked: reproducibility.
- Quality criterion checked: traceability.

## Safety and authority
- Respect user authorization, privacy, confidentiality, intellectual property, and applicable law.
- Ask for confirmation before irreversible, external, destructive, or financially consequential actions.
- Require explicit user confirmation and appropriate authorization before external, destructive, irreversible, or financially consequential actions.
- Minimize data, use only authorized information, do not expose secrets or personal data, and preserve confidentiality.

## Do not
- Do not use when the named skill is irrelevant to the requested outcome merely because a keyword appears in the conversation.
- Do not fabricate access, experience, credentials, measurements, sources, calculations, or completed actions.
- Do not continue with material ambiguity when a missing answer would change the result; request the minimum clarification needed.
- Answering before defining the actual outcome and decision context.
- Treating assumptions, examples, or model memory as verified facts.
- Producing generic advice without a concrete artifact, acceptance criteria, or next action.
- Ignoring missing data, source quality, uncertainty, constraints, or stakeholder authority.

## Progressive disclosure
- Read [references/knowledge.md](references/knowledge.md) for concepts, source rules, tools, and domain controls.
- Read [references/workflow.md](references/workflow.md) for the full operating procedure, failure handling, and handoff.
- Read [references/evaluation.md](references/evaluation.md) before finalizing high-stakes or production work.
- Read [examples/examples.md](examples/examples.md) when examples or output patterns are needed.
- Use [assets/output-template.md](assets/output-template.md) as the default deliverable structure.
- Validate structured inputs and outputs against the JSON Schemas in `schemas/` when integrating programmatically.

## Recommended companion skills
- $data-driven-operator
- $evidence-seeking-skeptic
- $detail-oriented-craftsperson
- $quantitative-reasoning
- $evidence-weighting
- $bias-detection
- $data-storytelling
- $executive-communication
- $data-exploration
- $descriptive-statistics
- $decision-log-management

## Invocation arguments
Apply this skill to the user's current request. When the request is incomplete, infer only low-risk formatting preferences and ask for material missing context.
