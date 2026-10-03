# v0.1.0 validation record

Date: 2026-10-03. Scope: skill packaging, selected report invariants, one independent offline synthetic workflow test, and retrieval connectivity. No real-paper accuracy benchmark has been completed.

## Implemented checks

- Skill-creator frontmatter/naming/scaffold validation.
- Distribution files, internal skill references, invocation metadata and absence of machine-specific paths in the installed package.
- 21 automated test methods for report linking, source inspection levels, strong-label requirements, unknown independent units, reference-list versus in-text attribution, independent discovery versus citations, connected root traces, cycles, blocked tasks, malformed input and CLI exit codes.
- Synthetic JSON example passes structural checks. One test intentionally demonstrates that even structurally valid strong labels can be scientifically wrong: the checker does not read or reason over the claim's meaning.

## Independent offline workflow test

A separate Codex agent was given only the skill and an invented source packet, without the expected-outcome examples. The packet contained an overextended review claim, a mouse intervention/knockout study, a docking abstract and a juvenile-animal marker abstract. External retrieval was disabled for that test.

The resulting report retained the observed review-to-study edge, separated independent materials from that edge, and did not claim that docking proved binding, mouse ejection fraction established patient mortality reduction, or a noncomparable marker result constituted direct counterevidence. The review also identified two wording ambiguities: partial support across species/outcomes and “not reported” inferred from an excerpt. Both rules were tightened before release.

This is one synthetic execution plus review, not an estimate of sensitivity, specificity, accuracy, or reliable real-world performance. The revised wording was checked for package consistency; no new large behavioral benchmark is implied.

## Retrieval smoke test

An existing configured Biomni direct-tool bridge was inspected through status and catalog, then `literature.query_europepmc` was called with `query=TITLE:citations AND TITLE:evidence` and `max_results=1`. The current call completed successfully and returned Europe PMC metadata. The private local receipt was retained outside this repository.

This proves a single metadata retrieval route worked in the developer's environment on the test date. It does not establish full-text access, citation-chain correctness, portability to another environment, or verification of any returned paper's findings.

## Remaining work

Evaluate an expert-annotated real-paper set, including unavailable full text, ambiguous citation placement, conflicting models, null findings, corrections/retractions and incomplete mechanisms. Record overclaiming errors, evidence-location errors and blocked cases before making performance claims.
