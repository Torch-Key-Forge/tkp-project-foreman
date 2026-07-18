
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "project_foreman" / "data"

class ProjectForemanTests(unittest.TestCase):
    @staticmethod
    def load(name):
        return json.loads((DATA / name).read_text(encoding="utf-8"))

    def test_fixture_turn_count(self):
        fixture = self.load("atlas_workshop_conversation.json")
        self.assertEqual(len(fixture["turns"]), 132)

    def test_spine_count(self):
        spine = self.load("Project_Spine.json")
        self.assertEqual(len(spine["spine_events"]), 10)

    def test_authority_count(self):
        ledger = self.load("Authority_Ledger.json")
        self.assertEqual(len(ledger["entries"]), 6)

    def test_all_claim_refs_resolve(self):
        trace = self.load("Source_Trace_Index.json")
        refs = {x["source_ref"] for x in trace["source_turns"]}
        for claim in trace["claim_links"]:
            for ref in claim["source_refs"]:
                self.assertIn(ref, refs)

    def test_authority_refs_match_operator_evidence(self):
        ledger = self.load("Authority_Ledger.json")
        trace = self.load("Source_Trace_Index.json")
        sources = {x["source_ref"]: x for x in trace["source_turns"]}
        expected = {
            "AUTH-001": "SRC-ATLAS-TURN-0024",
            "AUTH-002": "SRC-ATLAS-TURN-0057",
            "AUTH-003": "SRC-ATLAS-TURN-0070",
            "AUTH-004": "SRC-ATLAS-TURN-0096",
            "AUTH-005": "SRC-ATLAS-TURN-0098",
            "AUTH-006": "SRC-ATLAS-TURN-0106",
        }
        for entry in ledger["entries"]:
            ref = entry["source_refs"][0]
            source = sources[ref]
            self.assertEqual(ref, expected[entry["ledger_id"]])
            self.assertEqual(source["role"], "user")
            self.assertIn(entry["statement"], source["text"])

    def test_spine_refs_match_reviewed_semantic_map(self):
        spine = self.load("Project_Spine.json")
        expected = {
            "SPINE-001": ["SRC-ATLAS-TURN-0001", "SRC-ATLAS-TURN-0003", "SRC-ATLAS-TURN-0005"],
            "SPINE-002": ["SRC-ATLAS-TURN-0011", "SRC-ATLAS-TURN-0017", "SRC-ATLAS-TURN-0020"],
            "SPINE-003": ["SRC-ATLAS-TURN-0024"],
            "SPINE-004": ["SRC-ATLAS-TURN-0049", "SRC-ATLAS-TURN-0057"],
            "SPINE-005": ["SRC-ATLAS-TURN-0062", "SRC-ATLAS-TURN-0064"],
            "SPINE-006": ["SRC-ATLAS-TURN-0070"],
            "SPINE-007": ["SRC-ATLAS-TURN-0080", "SRC-ATLAS-TURN-0082", "SRC-ATLAS-TURN-0090"],
            "SPINE-008": ["SRC-ATLAS-TURN-0096"],
            "SPINE-009": ["SRC-ATLAS-TURN-0098"],
            "SPINE-010": ["SRC-ATLAS-TURN-0109", "SRC-ATLAS-TURN-0110", "SRC-ATLAS-TURN-0104"],
        }
        for event in spine["spine_events"]:
            self.assertEqual(event["source_refs"], expected[event["event_id"]])

    def test_claim_links_match_artifact_source_refs(self):
        spine = self.load("Project_Spine.json")
        ledger = self.load("Authority_Ledger.json")
        continuation = self.load("Continuation_Brief.json")
        trace = self.load("Source_Trace_Index.json")
        links = {x["claim_id"]: x["source_refs"] for x in trace["claim_links"]}
        for event in spine["spine_events"]:
            self.assertEqual(links[event["event_id"]], event["source_refs"])
        for entry in ledger["entries"]:
            self.assertEqual(links[entry["ledger_id"]], entry["source_refs"])
        self.assertEqual(links["CONT-001"], continuation["source_refs"])

    def test_production_boundary_points_to_direct_operator_turn(self):
        continuation = self.load("Continuation_Brief.json")
        trace = self.load("Source_Trace_Index.json")
        sources = {x["source_ref"]: x for x in trace["source_turns"]}
        ref = continuation["source_refs"][1]
        source = sources[ref]
        self.assertEqual(ref, "SRC-ATLAS-TURN-0098")
        self.assertEqual(source["role"], "user")
        self.assertIn("Production deployment remains unauthorized", source["text"])

if __name__ == "__main__":
    unittest.main()
