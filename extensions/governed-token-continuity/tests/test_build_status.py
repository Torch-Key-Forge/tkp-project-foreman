from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from build_status.engine import evaluate_board, load_config, snapshot_to_dict
from build_status.model import CardState


class BuildStatusTests(unittest.TestCase):
    def make_config(self, root: Path) -> Path:
        payload = {
            "project": {"id": "T", "name": "Test", "current_gate": "G1", "return_point": "review"},
            "holds": [{"id": "future", "title": "Future work", "active": True}],
            "cards": [
                {
                    "id": "A",
                    "title": "First",
                    "done_when": {"all": [{"label": "acceptance", "path": "a.accepted"}]},
                    "review_when": {"all": [{"label": "output", "path": "a.out"}]},
                    "active_when": {"any": [{"label": "work", "path": "a.work"}]}
                },
                {
                    "id": "B",
                    "title": "Second",
                    "dependencies": ["A"],
                    "done_when": {"all": [{"label": "acceptance", "path": "b.accepted"}]}
                },
                {
                    "id": "C",
                    "title": "Held",
                    "dependencies": ["B"],
                    "blocked_by_holds": ["future"],
                    "done_when": {"all": [{"label": "acceptance", "path": "c.accepted"}]}
                }
            ]
        }
        path = root / "board.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_lifecycle_is_evidence_driven(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_config(self.make_config(root))

            snap = evaluate_board(config, root)
            self.assertEqual(snap.cards[0].state, CardState.READY)
            self.assertEqual(snap.cards[1].state, CardState.PLANNED)
            self.assertEqual(snap.cards[2].state, CardState.BLOCKED)

            (root / "a.work").write_text("started", encoding="utf-8")
            self.assertEqual(evaluate_board(config, root).cards[0].state, CardState.ACTIVE)

            (root / "a.out").write_text("built", encoding="utf-8")
            self.assertEqual(evaluate_board(config, root).cards[0].state, CardState.REVIEW)

            (root / "a.accepted").write_text("accepted", encoding="utf-8")
            snap = evaluate_board(config, root)
            self.assertEqual(snap.cards[0].state, CardState.DONE)
            self.assertEqual(snap.cards[1].state, CardState.READY)

    def test_machine_snapshot_is_serializable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = evaluate_board(load_config(self.make_config(root)), root)
            encoded = json.dumps(snapshot_to_dict(snapshot))
            self.assertIn('"counts"', encoded)

    def test_unknown_dependency_fails_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "bad.json"
            path.write_text(json.dumps({"cards": [{"id": "A", "title": "A", "dependencies": ["X"]}]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
