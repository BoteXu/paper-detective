#!/usr/bin/env python3
"""Check report structure and selected evidence constraints, never scientific truth."""
import argparse
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

RELATIONS = {"direct_support", "partial_support", "indirect", "contradicts", "insufficient"}
INSPECTIONS = {"metadata_only", "abstract_inspected", "excerpt_inspected", "full_text_inspected", "complete_materials_inspected", "unavailable"}
CONTEXT = {"subject", "species", "model", "assay", "biological_unit", "sample_size", "contrast", "outcome", "uncertainty"}
UNKNOWN = {"not_reported", "not_retrieved", "not_applicable", "not_provided_in_inspected_materials"}


def is_text(value):
    return isinstance(value, str) and bool(value.strip())


def is_choice(value, choices):
    return isinstance(value, str) and value in choices


def validate(report):
    errors = []

    def fail(path, message):
        errors.append(f"{path}: {message}")

    def text_field(obj, field, path):
        if not is_text(obj.get(field)):
            fail(f"{path}.{field}", "requires a nonempty string")

    def string_list(value, path, nonempty=False):
        if not isinstance(value, list) or any(not is_text(x) for x in value):
            fail(path, "requires an array of nonempty strings")
        elif nonempty and not value:
            fail(path, "must include at least one limitation")

    def records(field, nonempty=False):
        value = report.get(field)
        if not isinstance(value, list):
            fail(field, "requires an array")
            return []
        if nonempty and not value:
            fail(field, "must not be empty")
        result = []
        for i, item in enumerate(value):
            if not isinstance(item, dict):
                fail(f"{field}[{i}]", "requires an object")
            else:
                result.append((f"{field}[{i}]", item))
        return result

    def keyed(items):
        result = {}
        for path, item in items:
            key = item.get("id")
            if not is_text(key):
                fail(f"{path}.id", "requires a nonempty string")
            elif key in result:
                fail(f"{path}.id", "duplicate ID")
            else:
                result[key] = item
        return result

    def link(value, targets, path, nullable=False):
        if nullable and value is None:
            return None
        if not is_text(value) or value not in targets:
            fail(path, "unresolved ID")
            return None
        return targets[value]

    def enum(obj, field, choices, path):
        value = obj.get(field)
        if not isinstance(value, str) or value not in choices:
            fail(f"{path}.{field}", "invalid or missing value")

    if not isinstance(report, dict):
        return ["report: requires an object"]
    if report.get("schema_version") != "1.0.0":
        fail("schema_version", "expected 1.0.0")
    enum(report, "mode", {"claim-check", "citation-trace"}, "report")
    text_field(report, "input_claim", "report")
    stamp = report.get("as_of")
    try:
        if not isinstance(stamp, str) or len(stamp) != 10:
            raise ValueError
        date.fromisoformat(stamp)
    except ValueError:
        fail("as_of", "expected a valid YYYY-MM-DD date")
    string_list(report.get("limitations"), "limitations", nonempty=True)

    claim_rows = records("claims", nonempty=True)
    source_rows = records("sources")
    evidence_rows = records("evidence")
    edge_rows = records("citation_edges")
    log_rows = records("search_log")
    claims, sources = keyed(claim_rows), keyed(source_rows)
    keyed(evidence_rows)

    for path, claim in claim_rows:
        text_field(claim, "text", path)
        text_field(claim, "conclusion", path)
        string_list(claim.get("gaps"), f"{path}.gaps")

    for path, source in source_rows:
        text_field(source, "title", path)
        text_field(source, "status_check", path)
        enum(source, "source_type", {"original_research", "review", "other"}, path)
        enum(source, "identity_status", {"verified", "provided_material", "unresolved"}, path)
        enum(source, "inspection", INSPECTIONS, path)
        for field in ("identifier", "url"):
            if field not in source or (source[field] is not None and not is_text(source[field])):
                fail(f"{path}.{field}", "requires a nonempty string or null")
        url = source.get("url")
        if is_text(url):
            try:
                parsed = urlparse(url)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    raise ValueError
            except ValueError:
                fail(f"{path}.url", "expected an HTTP(S) URL")

    covered = set()
    for path, evidence in evidence_rows:
        claim = link(evidence.get("claim_id"), claims, f"{path}.claim_id")
        source = link(evidence.get("source_id"), sources, f"{path}.source_id")
        if claim is not None:
            covered.add(evidence["claim_id"])
        enum(evidence, "relation", RELATIONS, path)
        text_field(evidence, "result", path)
        text_field(evidence, "rationale", path)
        location = evidence.get("location")
        if "location" not in evidence or (location is not None and not is_text(location)):
            fail(f"{path}.location", "requires a nonempty string or null")
        relation = evidence.get("relation")
        if isinstance(relation, str) and relation in RELATIONS - {"insufficient"}:
            if not is_text(location):
                fail(f"{path}.location", "a substantive evidence relation requires a source location")
            if source is not None and is_choice(source.get("inspection"), {"metadata_only", "unavailable"}):
                fail(path, "uninspected source content cannot substantiate an evidence relation")
        context = evidence.get("context")
        if not isinstance(context, dict):
            fail(f"{path}.context", "requires an object")
            context = {}
        for field in sorted(CONTEXT):
            text_field(context, field, f"{path}.context")
        if isinstance(relation, str) and relation in {"direct_support", "contradicts"}:
            if source is not None:
                if source.get("source_type") != "original_research":
                    fail(path, "strong labels require original research")
                if not is_choice(source.get("identity_status"), {"verified", "provided_material"}):
                    fail(path, "strong labels require resolved/provided source identity")
                if not is_choice(source.get("inspection"), {"full_text_inspected", "complete_materials_inspected"}):
                    fail(path, "strong labels require inspected full text or complete original materials")
            for field in ("subject", "model", "assay", "biological_unit", "contrast", "outcome"):
                value = context.get(field)
                if isinstance(value, str) and value in UNKNOWN:
                    fail(f"{path}.context.{field}", "strong labels require known experimental context")

    for key, claim in claims.items():
        if key not in covered and not claim.get("gaps"):
            fail(f"claims.{key}", "a claim with no evidence must record its unresolved gap")

    if report.get("mode") == "citation-trace":
        link(report.get("root_source_id"), sources, "root_source_id")
    elif report.get("mode") == "claim-check":
        if "root_source_id" not in report or report.get("root_source_id") is not None:
            fail("root_source_id", "claim-check requires null")
        if edge_rows:
            fail("citation_edges", "claim-check cannot claim an actual citation trace")

    for path, edge in edge_rows:
        citing = link(edge.get("from_source_id"), sources, f"{path}.from_source_id")
        link(edge.get("to_source_id"), sources, f"{path}.to_source_id")
        link(edge.get("claim_id"), claims, f"{path}.claim_id", nullable=True)
        if "claim_id" not in edge:
            fail(f"{path}.claim_id", "requires an ID or explicit null")
        if edge.get("from_source_id") == edge.get("to_source_id"):
            fail(path, "self-citation edge is not a trace hop")
        enum(edge, "basis", {"in_text_citation", "reference_list"}, path)
        text_field(edge, "location", path)
        text_field(edge, "reference_marker", path)
        if "quote" not in edge or not isinstance(edge["quote"], str):
            fail(f"{path}.quote", "requires a string")
        if edge.get("basis") == "in_text_citation" and not is_text(edge.get("quote")):
            fail(f"{path}.quote", "in-text citation requires a short actual quote")
        if edge.get("basis") == "reference_list" and edge.get("claim_id") is not None:
            fail(path, "reference-list presence cannot be attached to a sentence-level claim")
        if citing is not None and not is_choice(citing.get("inspection"), {"excerpt_inspected", "full_text_inspected", "complete_materials_inspected"}):
            fail(path, "a citation edge requires inspection of the citing material")

    root = report.get("root_source_id")
    if report.get("mode") == "citation-trace" and is_text(root) and root in sources:
        reached = {root}
        changed = True
        while changed:
            changed = False
            for _, edge in edge_rows:
                a, b = edge.get("from_source_id"), edge.get("to_source_id")
                if is_text(a) and is_text(b) and a in reached and b in sources and b not in reached:
                    reached.add(b)
                    changed = True
        for path, edge in edge_rows:
            a = edge.get("from_source_id")
            if is_text(a) and a not in reached:
                fail(path, "citation edge is disconnected from the supplied root source")

    for path, entry in log_rows:
        for field in ("provider", "query", "notes"):
            text_field(entry, field, path)
        enum(entry, "status", {"completed", "failed", "not_run"}, path)
    return errors


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Not a JSON value: {value}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_keys, parse_constant=reject_constant)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Cannot read report: {exc}", file=sys.stderr)
        return 2
    errors = validate(report)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Structural checks passed. Source authenticity and scientific validity remain unverified by this checker.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
