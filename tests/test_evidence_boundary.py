import json
import unittest
from pathlib import Path

from project_foreman.evidence_bound_server import build_recovery_payload

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "project_foreman" / "data"
STATIC = ROOT / "project_foreman" / "static_evidence"


class EvidenceBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads(
            (DATA / "Evidence_Boundary.json").read_text(encoding="utf-8")
        )

    def test_policy_identity_and_mode(self):
        self.assertEqual(self.policy["policy_id"], "PF-EVIDENCE-BOUNDARY-001")
        self.assertEqual(self.policy["mode"], "EVIDENCE_BOUND")
        self.assertEqual(self.policy["public_rule"], "No source, no claim.")

    def test_no_assistant_authority_promotion(self):
        candidates = self.policy["candidate_handling"]
        self.assertEqual(candidates["default_status"], "PROVISIONAL_REVIEW")
        self.assertEqual(candidates["disposition"], "HELD_FOR_REVIEW")
        self.assertEqual(candidates["assistant_authority_promotion"], "NONE")
        self.assertEqual(candidates["promotion_rule"], "OPERATOR_REVIEW_REQUIRED")

    def test_execution_and_completion_are_not_inferred(self):
        execution = self.policy["execution_handling"]
        self.assertEqual(execution["command_without_completion_evidence"], "NOT_INFERRED")
        self.assertEqual(execution["completion_without_evidence"], "NOT_INFERRED")

    def test_sifting_states_are_explicit(self):
        states = {item["state"] for item in self.policy["sifting_states"]}
        self.assertEqual(
            states,
            {
                "CANONICAL_PROJECT_EVIDENCE",
                "PROVISIONAL_REVIEW",
                "UNRESOLVED",
                "SOURCE_UNAVAILABLE",
            },
        )

    def test_unsupported_claim_fails_closed(self):
        response = self.policy["fail_closed_response"]
        self.assertEqual(response["status"], "NOT_ESTABLISHED")
        self.assertIn("not established", response["message"].lower())

    def test_recovery_payload_includes_evidence_boundary(self):
        payload = build_recovery_payload()
        self.assertEqual(payload["evidence_boundary"]["mode"], "EVIDENCE_BOUND")

    def test_evidence_interface_assets_exist(self):
        for name in ("index.html", "app.js", "styles.css"):
            self.assertTrue((STATIC / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
