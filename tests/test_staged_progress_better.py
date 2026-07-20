import tempfile
import unittest
import zipfile
from pathlib import Path

from project_foreman import server as base
from project_foreman.evidence_bound_server import (
    EXPORT_STAGES,
    RECOVERY_STAGES,
    StageReporter,
    build_export_package,
    build_recovery_payload,
)


class StagedProgressBetterTests(unittest.TestCase):
    def test_reporter_emits_plan_running_and_pass(self):
        events = []
        reporter = StageReporter("TEST", (("one", "One"),), events.append)
        reporter.begin("one", "Starting.")
        reporter.complete("one", "Finished.", {"count": 1})

        self.assertEqual(events[0]["type"], "plan")
        self.assertEqual(events[0]["stage_total"], 1)
        self.assertEqual(events[1]["status"], "RUNNING")
        self.assertEqual(events[2]["status"], "PASS")
        self.assertEqual(events[2]["details"]["count"], 1)

    def test_recovery_emits_six_real_completed_stages(self):
        events = []
        payload = build_recovery_payload(progress=events.append)
        completed = [
            event
            for event in events
            if event.get("type") == "stage" and event.get("status") == "PASS"
        ]

        self.assertEqual(len(RECOVERY_STAGES), 6)
        self.assertEqual(len(completed), 6)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["evidence_boundary"]["mode"], "EVIDENCE_BOUND")
        self.assertEqual(
            [event["stage_id"] for event in completed],
            [stage_id for stage_id, _ in RECOVERY_STAGES],
        )

    def test_export_emits_six_stages_and_preserves_nine_file_contract(self):
        original_export_dir = base.EXPORT_DIR
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                base.EXPORT_DIR = Path(temp_dir)
                events = []
                result = build_export_package(progress=events.append)
                completed = [
                    event
                    for event in events
                    if event.get("type") == "stage" and event.get("status") == "PASS"
                ]

                self.assertEqual(len(EXPORT_STAGES), 6)
                self.assertEqual(len(completed), 6)
                self.assertTrue(result["validated"])
                self.assertEqual(result["file_count"], 9)
                self.assertTrue(Path(result["zip_path"]).is_file())

                with zipfile.ZipFile(result["zip_path"], "r") as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(len(archive.namelist()), 9)
        finally:
            base.EXPORT_DIR = original_export_dir

    def test_stage_plans_are_stable_and_unique(self):
        for stages in (RECOVERY_STAGES, EXPORT_STAGES):
            identifiers = [stage_id for stage_id, _ in stages]
            labels = [label for _, label in stages]
            self.assertEqual(len(identifiers), len(set(identifiers)))
            self.assertTrue(all(identifiers))
            self.assertTrue(all(labels))


if __name__ == "__main__":
    unittest.main()
