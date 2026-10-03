# Paper Detective

A Codex skill for checking what primary research actually supports a scientific claim.

Version **v0.1.0** provides a claim-checking and citation-tracing workflow, an evidence report template, and an optional standard-library JSON consistency checker. Retrieval and interpretation are performed by the host assistant and its available tools. This is not a standalone model, hosted app, or background service.

[中文说明](README.md) · [Skill](paper-detective/SKILL.md)

## Modes

- **Claim check:** a sentence without a source initiates candidate evidence discovery. Discovered papers are not presented as the sentence's actual citation history.
- **Citation trace:** a sentence plus a source paper/DOI/full text initiates an anchored citation trace. Independent evidence discovery is reported separately.

The workflow separates effects, receptor dependence, binding and mechanism; records species/model, assay, controls, independent units, reported results, source locations and evidence gaps; and distinguishes direct, partial, indirect, conflicting and insufficient evidence. Missing text and unsuccessful searches remain explicit.

Default budgets are two citation hops and fifteen candidate papers, adjustable by the user. A bounded trace is not a systematic review or a claim to have found the earliest-ever discovery.

## Install and invoke

Download the [skill ZIP](https://github.com/BoteXu/paper-detective/releases/download/v0.1.0/paper-detective-v0.1.0.zip) or clone this repository. Copy its inner `paper-detective/` directory into `$CODEX_HOME/skills/`, or `~/.codex/skills/` when `CODEX_HOME` is unset. Do not overwrite an existing skill without inspecting it. Start a fresh Codex session; restart the client if discovery has not refreshed.

```text
Use $paper-detective to check this scientific claim: <claim>.
Separate experimentally tested effects from mechanism and extrapolation.
```

```text
Use $paper-detective to trace the evidence for <sentence> in <paper DOI/link>.
Show anchored citation edges, primary experiments and unresolved branches.
```

The skill follows the user's language. It requires no particular MCP server or additional model key. Reuse configured Biomni direct tools for biomedical retrieval when available; otherwise use accessible official sources or user-provided materials. Without retrieval tools, the workflow is limited to provided material.

## Optional report checks

Python 3.10+; no additional packages:

```sh
python paper-detective/scripts/validate_report.py path/to/report.json
python -m unittest discover -s tests -v
```

See [report-format.md](paper-detective/references/report-format.md). Passing checks establishes structural consistency, not source authenticity or scientific validity.

## Validation boundary

Tests and examples use explicitly synthetic materials to exercise important failure modes. This version has not completed accuracy evaluation against an expert-annotated real-paper benchmark. Never treat synthetic examples as verified research, or automatically use the output for clinical decisions. Keep sensitive data and private receipts out of public endpoints and repositories; respect source licenses.

MIT License. Report issues with a sanitized, reproducible example.
