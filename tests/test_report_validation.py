"""Synthetic invariant tests; not an accuracy benchmark for the reasoning skill."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "paper-detective" / "scripts" / "validate_report.py"
spec = importlib.util.spec_from_file_location("validate_report", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def fixture():
    return json.loads((ROOT / "examples" / "synthetic-report.json").read_text(encoding="utf-8"))


def trace_fixture():
    report = fixture()
    report["mode"] = "citation-trace"
    report["root_source_id"] = "R"
    source = copy.deepcopy(report["sources"][0])
    source.update(id="R", title="Synthetic review", source_type="review", inspection="excerpt_inspected")
    report["sources"].append(source)
    report["citation_edges"] = [{
        "from_source_id": "R", "to_source_id": "S1", "basis": "in_text_citation",
        "location": "Synthetic page 2, paragraph 1", "reference_marker": "[7]",
        "quote": "Synthetic claim statement [7].", "claim_id": "C1"
    }]
    return report


class ReportTests(unittest.TestCase):
    def test_synthetic_indirect_evidence_is_valid(self):
        self.assertEqual(checker.validate(fixture()), [])

    def test_inspected_original_can_have_strong_label_structurally(self):
        report = fixture()
        report["evidence"][0]["relation"] = "direct_support"
        # This deliberately does not prove that the prose claim is scientifically supported.
        self.assertEqual(checker.validate(report), [])

    def test_abstract_cannot_substantiate_strong_label(self):
        for relation in ("direct_support", "contradicts"):
            with self.subTest(relation=relation):
                report = fixture()
                report["sources"][0]["inspection"] = "abstract_inspected"
                report["evidence"][0]["relation"] = relation
                self.assertTrue(checker.validate(report))

    def test_review_cannot_supply_primary_direct_support(self):
        report = fixture()
        report["sources"][0]["source_type"] = "review"
        report["evidence"][0]["relation"] = "direct_support"
        self.assertTrue(checker.validate(report))

    def test_unresolved_source_cannot_support_strong_label(self):
        report = fixture()
        report["sources"][0]["identity_status"] = "unresolved"
        report["evidence"][0]["relation"] = "direct_support"
        self.assertTrue(checker.validate(report))

    def test_dangling_claim_or_source_rejected(self):
        for key in ("claim_id", "source_id"):
            with self.subTest(key=key):
                report = fixture()
                report["evidence"][0][key] = "MISSING"
                self.assertTrue(checker.validate(report))

    def test_duplicate_ids_rejected(self):
        for field in ("claims", "sources", "evidence"):
            with self.subTest(field=field):
                report = fixture()
                report[field].append(copy.deepcopy(report[field][0]))
                self.assertTrue(checker.validate(report))

    def test_supported_relation_needs_location(self):
        report = fixture()
        report["evidence"][0]["location"] = None
        self.assertTrue(checker.validate(report))

    def test_wholly_blocked_report_can_be_valid(self):
        report = fixture()
        report["sources"] = []
        report["evidence"] = []
        self.assertEqual(checker.validate(report), [])
        report["claims"][0]["gaps"] = []
        self.assertTrue(checker.validate(report))

    def test_metadata_only_relation_must_be_insufficient(self):
        report = fixture()
        report["sources"][0]["inspection"] = "metadata_only"
        self.assertTrue(checker.validate(report))
        report["evidence"][0]["relation"] = "insufficient"
        report["evidence"][0]["location"] = None
        self.assertEqual(checker.validate(report), [])

    def test_unknown_independent_unit_blocks_strong_label(self):
        for value in ("not_reported", "not_provided_in_inspected_materials", "not_retrieved", "not_applicable"):
            with self.subTest(value=value):
                report = fixture()
                report["evidence"][0]["relation"] = "direct_support"
                report["evidence"][0]["context"]["biological_unit"] = value
                self.assertTrue(checker.validate(report))

    def test_anchored_trace_valid(self):
        self.assertEqual(checker.validate(trace_fixture()), [])

    def test_independent_discovery_is_not_citation_edge(self):
        report = trace_fixture()
        report["citation_edges"][0]["basis"] = "independent_search"
        self.assertTrue(checker.validate(report))

    def test_bibliography_does_not_establish_sentence_attribution(self):
        report = trace_fixture()
        edge = report["citation_edges"][0]
        edge.update(basis="reference_list", quote="", location="References [7]")
        self.assertTrue(checker.validate(report))
        edge["claim_id"] = None
        self.assertEqual(checker.validate(report), [])

    def test_claim_check_cannot_claim_trace(self):
        report = trace_fixture()
        report["mode"] = "claim-check"
        report["root_source_id"] = None
        self.assertTrue(checker.validate(report))

    def test_trace_root_and_intext_quote_required(self):
        report = trace_fixture()
        report["root_source_id"] = "MISSING"
        self.assertTrue(checker.validate(report))
        report = trace_fixture()
        report["citation_edges"][0]["quote"] = ""
        self.assertTrue(checker.validate(report))

    def test_disconnected_edge_rejected(self):
        report = trace_fixture()
        unrelated = copy.deepcopy(report["sources"][0])
        unrelated.update(id="U", inspection="full_text_inspected")
        report["sources"].append(unrelated)
        report["citation_edges"].append(dict(report["citation_edges"][0], from_source_id="U"))
        self.assertTrue(checker.validate(report))

    def test_real_cycle_can_be_recorded_without_infinite_loop(self):
        report = trace_fixture()
        edge = dict(report["citation_edges"][0], from_source_id="S1", to_source_id="R")
        report["citation_edges"].append(edge)
        self.assertEqual(checker.validate(report), [])

    def test_malformed_values_return_errors_not_tracebacks(self):
        for field in ("inspection", "identity_status", "source_type"):
            with self.subTest(field=field):
                report = trace_fixture()
                report["sources"][0][field] = []
                report["evidence"][0]["relation"] = "direct_support"
                self.assertTrue(checker.validate(report))
        for field in ("claims", "sources", "evidence", "citation_edges", "search_log"):
            report = fixture()
            report[field] = [None]
            self.assertTrue(checker.validate(report))

    def test_date_and_limits_are_required(self):
        report = fixture()
        report["as_of"] = "2026-02-30"
        report["limitations"] = []
        self.assertTrue(checker.validate(report))

    def test_cli_exit_codes_and_duplicate_json_keys(self):
        cases = [(json.dumps(fixture()), 0), ('{"mode":"x","mode":"y"}', 2), ('{"extra": NaN}', 2), ('[]', 1), ('{', 2)]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            for text, expected in cases:
                with self.subTest(text=text[:30]):
                    path.write_text(text, encoding="utf-8")
                    run = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
                    self.assertEqual(run.returncode, expected, run.stderr)
                    self.assertNotIn("Traceback", run.stderr)


if __name__ == "__main__":
    unittest.main()
