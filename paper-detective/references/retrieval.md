# Retrieval and source verification

Use the tools already available in the current environment. This skill has no mandatory MCP dependency and does not install packages, request model keys, or create a second reasoning agent.

## Biomni, when configured

For substantive biomedical work, inspect `biomni_status` and `biomni_tool_catalog` before choosing a specialist function. Filter the catalog for literature retrieval and inspect the actual parameter contract. Relevant functions may include `query_europepmc`, `fetch_open_access_article`, and DOI/supplement retrieval; names and availability depend on the installed bridge. Call a suitable explicit tool when it helps, through its advertised route.

Inspect `runtime_state`, `last_attempt_success`, dependency checks and returned receipts separately. A prior successful run or `import_ready` is not a successful current query. Prefer direct functions; avoid routes requiring another model just to retrieve records. If MCP is unavailable, use an already configured local bridge only after inspecting its CLI contract. Do not assume another user's machine paths or bridge version.

Retain exact parameters, retrieval date, errors, result identifiers and source receipt references locally. If available, `biomni_evidence_record` can link interpretations to receipts and context: species, model, assay, biological unit, contrast and limitations. Receipt integrity is not scientific validation. Share sanitized reports, not local configuration or private receipts.

## Official fallbacks

- [Europe PMC REST API](https://europepmc.org/RestfulWebService): search metadata, reference lists, citations and open-access full-text XML. Metadata access does not guarantee full text. Inspect cursor/pagination; bounded results are not an exhaustive search.
- [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/): resolve PubMed records and related identifiers; distinguish PubMed metadata from PMC full text.
- [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/): check DOI identity, bibliographic metadata and available relation/update information. Missing update metadata does not prove a paper has no correction or retraction.
- Publisher article pages and correction notices: verify the paper version, bibliographic identity, figures, supplements and reported status.

Use current official documentation if writing API calls. Respect service usage limits and full-text licensing. Never bypass access controls. A lawful user-provided PDF can be inspected locally. Do not publish the entire paper or unnecessary excerpts in a public report.

## Evidence search

Search exact wording plus entity synonyms, intervention and outcome terms. For mechanism claims, seek the experimental link needed for each subclaim rather than only collecting papers sharing the entities. Look for comparable contrary/negative results with neutral terms; a literal search for “negative” alone misses much of the relevant evidence. Record query variants and screening reasons.

DOI resolution confirms identity, not interpretation. Match references using DOI when available and otherwise title/author/year; mark unresolved or ambiguous matches. Do not silently assign a DOI to a plausible title. A reference list proves a paper-level edge; only a located in-text citation ties that edge to the sentence.

For each source record, distinguish metadata only, abstract inspected, provided excerpt inspected, full text inspected, and complete original materials inspected. Mark publisher figure image, caption, supplement and raw-data inspection separately in prose. Conflicting versions require a version-specific location.

## Incomplete retrieval

Record tool/API error separately from zero results. With a failed endpoint, switch to an available official source; after a bounded retry, continue with accessible materials and disclose missing coverage. Stop citation cycles with a visited-source set, and preserve blocked branches. Search discovery may identify earlier papers; never label one “the first ever” without appropriate historical coverage.
