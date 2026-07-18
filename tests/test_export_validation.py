
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from project_foreman import server

class ExportValidationTests(unittest.TestCase):
    def test_export_zip_is_valid_and_has_eight_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(server, "EXPORT_DIR", Path(tmp)):
                result = server.build_export_package()
                self.assertTrue(result["validated"])
                self.assertEqual(result["file_count"], 8)
                self.assertTrue(result["zip_path"].is_file())
                with zipfile.ZipFile(result["zip_path"], "r") as zf:
                    self.assertIsNone(zf.testzip())
                    self.assertEqual(len(zf.namelist()), 8)

if __name__ == "__main__":
    unittest.main()
