
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "project_foreman" / "data"

class ProjectForemanTests(unittest.TestCase):
    def test_fixture_turn_count(self):
        fixture = json.loads((DATA / "atlas_workshop_conversation.json").read_text(encoding="utf-8"))
        self.assertEqual(len(fixture["turns"]), 132)

    def test_spine_count(self):
        spine = json.loads((DATA / "Project_Spine.json").read_text(encoding="utf-8"))
        self.assertEqual(len(spine["spine_events"]), 10)

    def test_authority_count(self):
        ledger = json.loads((DATA / "Authority_Ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(len(ledger["entries"]), 6)

    def test_all_claim_refs_resolve(self):
        trace = json.loads((DATA / "Source_Trace_Index.json").read_text(encoding="utf-8"))
        refs = {x["source_ref"] for x in trace["source_turns"]}
        for claim in trace["claim_links"]:
            for ref in claim["source_refs"]:
                self.assertIn(ref, refs)

if __name__ == "__main__":
    unittest.main()
