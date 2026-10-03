# Machine-readable report format v1.0.0

JSON is optional. The human-readable report remains the main deliverable. Use JSON when reproducible evidence links, later UI work, or automated consistency checks are useful. The validator uses Python 3.10+ standard library, rejects duplicate JSON keys and checks the constraints below; it is not a general JSON Schema engine or a scientific validity check.

## Top-level fields

| Field | Type / meaning |
|---|---|
| `schema_version` | String `1.0.0` |
| `mode` | `claim-check` or `citation-trace` |
| `input_claim` | Nonempty input sentence |
| `as_of` | ISO date YYYY-MM-DD |
| `root_source_id` | Source ID for citation-trace; null for claim-check |
| `claims` | Nonempty array: unique `id`, `text`, `conclusion`, `gaps` (array of strings) |
| `sources` | Array of source records below; may be empty for a wholly blocked task |
| `evidence` | Array of evidence records below; may be empty if each claim records its unresolved gap |
| `citation_edges` | Actual bibliographic edges only; empty in claim-check |
| `search_log` | Array: `provider`, `query`, `status`, `notes`; status is `completed`, `failed`, or `not_run` |
| `limitations` | Nonempty array of nonempty strings: bounds, blocked branches and missing checks |

Do not place credentials or sensitive search terms in the report. Include retrieval dates, budgets, pagination and stopping reasons in log notes/limitations. Extra fields are allowed for future UI metadata, but the validator does not check them. No overall score is defined by this format.

## Sources

Required fields: `id`, `title`, `identifier` (string or null), `url` (HTTP(S) string or null), `source_type`, `identity_status`, `inspection`, `status_check`.

- `source_type`: `original_research`, `review`, `other`.
- `identity_status`: `verified`, `provided_material`, `unresolved`. Public identifiers need external verification; a local user-provided document can use `provided_material` without claiming public identity verification. `identifier` may contain a private local ID in a local-only report; sanitize before sharing.
- `inspection`: `metadata_only`, `abstract_inspected`, `excerpt_inspected`, `full_text_inspected`, `complete_materials_inspected`, `unavailable`. These describe actual inspection, not availability.
- `status_check`: nonempty text explaining version, correction/retraction checks and unperformed checks.

## Evidence records

Required fields: unique `id`, `claim_id`, `source_id`, `relation`, `location` (string or null), `result`, `rationale`, `context`.

`relation`: `direct_support`, `partial_support`, `indirect`, `contradicts`, `insufficient`. Only `insufficient` may omit a source location or point to uninspected content. A source may support one claim and be insufficient for another; use separate evidence records. Every claim must have evidence or an explicit gap explaining why none is available.

`context` requires nonempty strings for `subject`, `species`, `model`, `assay`, `biological_unit`, `sample_size`, `contrast`, `outcome`, `uncertainty`. Use `not_reported` only after inspecting sufficient original materials to confirm the absence; use `not_provided_in_inspected_materials` for absence from an abstract/excerpt, `not_retrieved` for unavailable content, or `not_applicable` when appropriate. Explain clinically/scientifically significant missing fields in rationale/gaps. Strings allow sample hierarchy, denominators and reported intervals without forcing unsupported numerical precision.

Strong labels `direct_support` and `contradicts` require an original-research source, resolved/provided identity, and inspected full text or complete original materials, plus known `subject`, `model`, `assay`, `biological_unit`, `contrast` and `outcome`. For other labels, known limitations can be recorded even with partial text. Abstract-only claims remain provisional in prose. These structural gates do not determine whether the experiment truly supports or contradicts the claim.

## Citation edges

Required: `from_source_id`, `to_source_id`, `basis`, `location`, `reference_marker`, `quote`, `claim_id` (ID or null).

- `basis`: `in_text_citation` or `reference_list`. Independent search discovery is never a citation basis.
- In-text edges need a short actual quote, a reference marker and location from the citing paper. Attach `claim_id` only when its relationship to the target claim has been established.
- Reference-list edges need a reference-list location and marker, but `claim_id` must be null: bibliographic presence alone cannot establish sentence-level attribution.
- The citing source must have inspected excerpt/full text/complete materials. The cited source can be unavailable or unresolved; that blocks further interpretation, not the observed edge.
- Self-edges are rejected. Cycles between different sources may be real; stop traversing visited nodes and disclose the cycle rather than rewriting history.
- Every edge must be reachable from the supplied root source. A separate discovery chain belongs in supplemental analysis rather than the declared root trace.

## Run

```sh
python paper-detective/scripts/validate_report.py path/to/report.json
```

Exit 0 means the implemented structural checks passed; exit 1 means inconsistent report content; exit 2 means file, encoding or JSON syntax failure. The script does not make network requests or modify the report. The [synthetic JSON example](../../examples/synthetic-report.json) is for format demonstration only, not evidence of scientific validation.
