import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "project_foreman" / "data"


def load_json(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


class ProjectForemanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = load_json("atlas_workshop_conversation.json")
        cls.spine = load_json("Project_Spine.json")
        cls.ledger = load_json("Authority_Ledger.json")
        cls.continuation = load_json("Continuation_Brief.json")
        cls.trace = load_json("Source_Trace_Index.json")
        cls.sources = {x["source_ref"]: x for x in cls.trace["source_turns"]}
        cls.claims = {x["claim_id"]: x for x in cls.trace["claim_links"]}

    def test_fixture_turn_count(self):
        self.assertEqual(len(self.fixture["turns"]), 132)

    def test_spine_count(self):
        self.assertEqual(len(self.spine["spine_events"]), 10)

    def test_authority_count(self):
        self.assertEqual(len(self.ledger["entries"]), 6)

    def test_all_claim_refs_resolve(self):
        for claim in self.trace["claim_links"]:
            for ref in claim["source_refs"]:
                self.assertIn(ref, self.sources)

    def test_trace_claim_links_match_artifact_refs(self):
        for event in self.spine["spine_events"]:
            self.assertEqual(
                self.claims[event["event_id"]]["source_refs"],
                event["source_refs"],
            )
        for entry in self.ledger["entries"]:
            self.assertEqual(
                self.claims[entry["ledger_id"]]["source_refs"],
                entry["source_refs"],
            )
        self.assertEqual(
            self.claims["CONT-001"]["source_refs"],
            self.continuation["source_refs"],
        )

    def test_authority_entries_open_operator_evidence(self):
        for entry in self.ledger["entries"]:
            source = self.sources[entry["source_refs"][0]]
            self.assertEqual(source["role"], "user", entry["ledger_id"])
            self.assertIn(entry["statement"], source["text"], entry["ledger_id"])

    def test_demo_critical_first_source_semantics(self):
        expectations = {
            "SPINE-003": ("user", "AUTHORIZE_ATLAS_WORKSHOP_LOCAL_READ_ONLY_PROTOTYPE"),
            "SPINE-004": ("user", "export the project brief as a polished PDF"),
            "SPINE-005": ("user", "failed because the path is hardcoded"),
            "SPINE-006": ("user", "AUTHORIZE_ATLAS_WORKSHOP_PATH_RESOLUTION_REPAIR"),
            "SPINE-007": ("assistant", "repaired prototype completed the fixture run"),
            "SPINE-008": ("user", "ACCEPT_ATLAS_WORKSHOP_FIXTURE_TESTED_LOCAL_BASELINE"),
            "SPINE-009": ("user", "Production deployment remains unauthorized"),
            "SPINE-010": ("user", "operator interface and clean-checkout test are complete"),
        }
        for claim_id, (role, text_fragment) in expectations.items():
            source_ref = self.claims[claim_id]["source_refs"][0]
            source = self.sources[source_ref]
            self.assertEqual(source["role"], role, claim_id)
            self.assertIn(text_fragment, source["text"], claim_id)

    def test_continuation_demo_boundary_opens_operator_prohibition(self):
        acceptance = self.sources[self.continuation["source_refs"][0]]
        boundary = self.sources[self.continuation["source_refs"][1]]
        self.assertEqual(acceptance["role"], "user")
        self.assertIn("ACCEPT_ATLAS_WORKSHOP_FIXTURE_TESTED_LOCAL_BASELINE", acceptance["text"])
        self.assertEqual(boundary["role"], "user")
        self.assertIn("Production deployment remains unauthorized", boundary["text"])


if __name__ == "__main__":
    unittest.main()
