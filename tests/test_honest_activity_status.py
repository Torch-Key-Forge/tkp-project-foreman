import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "project_foreman" / "static_evidence"


class HonestActivityStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (STATIC / "index.html").read_text(encoding="utf-8")
        cls.js = (STATIC / "app.js").read_text(encoding="utf-8")
        cls.css = (STATIC / "styles.css").read_text(encoding="utf-8")

    def test_accessible_status_region_and_state_fields_exist(self):
        for token in (
            'role="status"',
            'aria-live="polite"',
            'aria-busy="false"',
            'data-state="IDLE"',
            'id="statusState"',
            'id="statusOperation"',
            'id="statusElapsed"',
            'id="statusMessage"',
        ):
            self.assertIn(token, self.html)

    def test_state_model_is_explicit(self):
        for state in ("IDLE", "RUNNING", "PASS", "FAIL"):
            self.assertIn(f'"{state}"', self.js)

    def test_good_fallback_and_better_stage_progress_coexist(self):
        self.assertIn("activity-track", self.html)
        self.assertIn("activity-bar", self.html)
        self.assertIn("status-running .activity-bar", self.css)
        self.assertIn('role="progressbar"', self.html)
        self.assertIn('aria-valuenow="0"', self.html)
        self.assertIn("completed / total", self.js)
        self.assertNotIn("estimatedTimeRemaining", self.js)

    def test_controls_are_locked_during_activity(self):
        self.assertIn("activityRunning", self.js)
        self.assertIn("syncActionAvailability", self.js)
        self.assertIn("loadBtn.disabled = activityRunning", self.js)
        self.assertIn("recoverBtn.disabled = activityRunning", self.js)
        self.assertIn("exportBtn.disabled = activityRunning || !recovery", self.js)

    def test_elapsed_timer_and_error_recovery_exist(self):
        self.assertIn("formatElapsed", self.js)
        self.assertIn("window.setInterval(updateElapsed, 250)", self.js)
        self.assertIn('finishActivity("FAIL"', self.js)
        self.assertIn("Review the", self.js)
        self.assertIn("retry", self.js)

    def test_reduced_motion_fallback_exists(self):
        self.assertIn("prefers-reduced-motion: reduce", self.css)
        self.assertIn("animation: none", self.css)
        self.assertIn("prefers-reduced-motion:reduce", self.html)

    def test_stream_routes_and_dynamic_export_count_are_preserved(self):
        for route in (
            "/api/fixture",
            "/api/recover/stream",
            "/api/export/stream",
        ):
            self.assertIn(route, self.js)
        self.assertIn("result.file_count", self.js)


if __name__ == "__main__":
    unittest.main()
