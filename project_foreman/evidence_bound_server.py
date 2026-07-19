from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from project_foreman import server as base

EVIDENCE_BOUNDARY_FILE = base.DATA_DIR / "Evidence_Boundary.json"
EVIDENCE_STATIC_DIR = base.PACKAGE_ROOT / "static_evidence"

_base_build_recovery_payload = base.build_recovery_payload
_base_build_export_package = base.build_export_package


def build_recovery_payload():
    payload = _base_build_recovery_payload()
    payload["evidence_boundary"] = base.load_json(EVIDENCE_BOUNDARY_FILE)
    return payload


def build_export_package() -> dict:
    result = _base_build_export_package()
    run_dir = Path(result["folder_path"])
    final_zip = Path(result["zip_path"])

    shutil.copy2(EVIDENCE_BOUNDARY_FILE, run_dir / "Evidence_Boundary.json")

    manifest_path = run_dir / "Manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["evidence_boundary_policy"] = "PF-EVIDENCE-BOUNDARY-001"
    manifest["evidence_mode"] = "EVIDENCE_BOUND"
    manifest["files"] = []

    for path in sorted(run_dir.iterdir()):
        if path.is_file() and path.name not in {"Manifest.json", "CHECKSUMS.sha256"}:
            manifest["files"].append(
                {
                    "name": path.name,
                    "sha256": base.sha256_file(path),
                    "size_bytes": path.stat().st_size,
                }
            )

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    checksum_path = run_dir / "CHECKSUMS.sha256"
    checksums = []
    for path in sorted(run_dir.iterdir()):
        if path.is_file() and path.name != "CHECKSUMS.sha256":
            checksums.append(f"{base.sha256_file(path)}  {path.name}")
    checksum_path.write_text("\n".join(checksums) + "\n", encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="project_foreman_evidence_export_") as temp_dir:
        temp_zip = Path(temp_dir) / final_zip.name
        with zipfile.ZipFile(
            temp_zip,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=True,
        ) as zf:
            for path in sorted(run_dir.iterdir()):
                if path.is_file():
                    zf.write(path, arcname=f"{run_dir.name}/{path.name}")

        with zipfile.ZipFile(temp_zip, "r") as zf:
            bad_member = zf.testzip()
            names = zf.namelist()

        if bad_member is not None:
            raise RuntimeError(f"Evidence-bound ZIP validation failed at member: {bad_member}")
        if len(names) != 9:
            raise RuntimeError(
                f"Evidence-bound ZIP validation expected 9 files but found {len(names)}."
            )

        if final_zip.exists():
            final_zip.unlink()
        shutil.move(str(temp_zip), str(final_zip))

    return {
        "zip_path": final_zip,
        "folder_path": run_dir,
        "sha256": base.sha256_file(final_zip),
        "file_count": 9,
        "validated": True,
    }


def main():
    base.STATIC_DIR = EVIDENCE_STATIC_DIR
    base.build_recovery_payload = build_recovery_payload
    base.build_export_package = build_export_package
    base.main()


if __name__ == "__main__":
    main()
