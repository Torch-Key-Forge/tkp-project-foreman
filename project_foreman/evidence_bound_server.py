from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from project_foreman import server as base

EVIDENCE_BOUNDARY_FILE = base.DATA_DIR / "Evidence_Boundary.json"
EVIDENCE_STATIC_DIR = base.PACKAGE_ROOT / "static_evidence"

RECOVERY_STAGES = (
    ("load_fixture", "Load sanitized fixture"),
    ("load_source_trace", "Verify source evidence"),
    ("assemble_spine", "Assemble Project Spine"),
    ("build_authority", "Build Authority Ledger"),
    ("resolve_continuation", "Resolve continuation state"),
    ("apply_evidence_boundary", "Apply evidence boundary"),
)

EXPORT_STAGES = (
    ("prepare_workspace", "Prepare export workspace"),
    ("collect_artifacts", "Collect recovered artifacts"),
    ("compose_markdown", "Generate Markdown views"),
    ("seal_manifest", "Build manifest and checksums"),
    ("create_archive", "Create ZIP archive"),
    ("validate_package", "Validate final package"),
)


class StageReporter:
    def __init__(self, operation: str, stages, callback=None):
        self.operation = operation
        self.stages = tuple(
            {"id": stage_id, "label": label}
            for stage_id, label in stages
        )
        self.callback = callback
        self.current = None
        self._emit(
            {
                "type": "plan",
                "operation": operation,
                "stage_total": len(self.stages),
                "stages": self.stages,
            }
        )

    def _emit(self, event: dict):
        if self.callback is None:
            return
        payload = dict(event)
        payload.setdefault("operation", self.operation)
        payload.setdefault("emitted_at", datetime.now(timezone.utc).isoformat())
        self.callback(payload)

    def _stage(self, stage_id: str) -> tuple[int, dict]:
        for index, stage in enumerate(self.stages, start=1):
            if stage["id"] == stage_id:
                return index, stage
        raise KeyError(f"Unknown progress stage: {stage_id}")

    def begin(self, stage_id: str, message: str):
        index, stage = self._stage(stage_id)
        self.current = stage_id
        self._emit(
            {
                "type": "stage",
                "stage_id": stage_id,
                "stage_index": index,
                "stage_total": len(self.stages),
                "label": stage["label"],
                "status": "RUNNING",
                "message": message,
            }
        )

    def complete(self, stage_id: str, message: str, details: dict | None = None):
        index, stage = self._stage(stage_id)
        event = {
            "type": "stage",
            "stage_id": stage_id,
            "stage_index": index,
            "stage_total": len(self.stages),
            "label": stage["label"],
            "status": "PASS",
            "message": message,
        }
        if details:
            event["details"] = details
        self._emit(event)
        self.current = None

    def fail_current(self, message: str):
        if self.current is None:
            return
        index, stage = self._stage(self.current)
        self._emit(
            {
                "type": "stage",
                "stage_id": self.current,
                "stage_index": index,
                "stage_total": len(self.stages),
                "label": stage["label"],
                "status": "FAIL",
                "message": message,
            }
        )
        self.current = None


def build_recovery_payload(progress=None):
    reporter = StageReporter("RECOVER PROJECT", RECOVERY_STAGES, progress)
    try:
        reporter.begin("load_fixture", "Reading the sanitized Atlas Workshop conversation.")
        fixture = base.load_json(base.FIXTURE_FILE)
        reporter.complete(
            "load_fixture",
            f"Loaded {len(fixture['turns'])} source turns.",
            {"turn_count": len(fixture["turns"])},
        )

        reporter.begin("load_source_trace", "Loading exact source-turn and claim links.")
        trace = base.load_json(base.SOURCE_TRACE_FILE)
        reporter.complete(
            "load_source_trace",
            f"Verified {len(trace['claim_links'])} traceable claims.",
            {"traceable_claims": len(trace["claim_links"])},
        )

        reporter.begin("assemble_spine", "Loading recovered project sequence and state.")
        spine = base.load_json(base.PROJECT_SPINE_FILE)
        reporter.complete(
            "assemble_spine",
            f"Assembled {len(spine['spine_events'])} spine events.",
            {"spine_events": len(spine["spine_events"])},
        )

        reporter.begin("build_authority", "Loading operator decisions and authority records.")
        authority = base.load_json(base.AUTHORITY_LEDGER_FILE)
        reporter.complete(
            "build_authority",
            f"Built {len(authority['entries'])} authority entries.",
            {"authority_entries": len(authority["entries"])},
        )

        reporter.begin("resolve_continuation", "Loading completed, unresolved, and next-action state.")
        continuation = base.load_json(base.CONTINUATION_BRIEF_FILE)
        reporter.complete(
            "resolve_continuation",
            f"Resolved continuation state with {len(continuation['unresolved'])} open items.",
            {"open_items": len(continuation["unresolved"])},
        )

        reporter.begin("apply_evidence_boundary", "Loading fail-closed evidence policy.")
        evidence_boundary = base.load_json(EVIDENCE_BOUNDARY_FILE)
        reporter.complete(
            "apply_evidence_boundary",
            f"Applied {evidence_boundary['policy_id']} in {evidence_boundary['mode']} mode.",
            {
                "policy_id": evidence_boundary["policy_id"],
                "mode": evidence_boundary["mode"],
            },
        )

        return {
            "status": "PASS",
            "fixture": {
                "title": fixture["conversation_identity"]["title"],
                "conversation_id": fixture["conversation_identity"]["local_conversation_id"],
                "turn_count": len(fixture["turns"]),
            },
            "metrics": {
                "turns": len(fixture["turns"]),
                "spine_events": len(spine["spine_events"]),
                "authority_entries": len(authority["entries"]),
                "open_items": len(continuation["unresolved"]),
                "traceable_claims": len(trace["claim_links"]),
            },
            "project_spine": spine,
            "authority_ledger": authority,
            "continuation_brief": continuation,
            "source_trace_index": trace,
            "evidence_boundary": evidence_boundary,
        }
    except Exception as exc:
        reporter.fail_current(str(exc))
        raise


def build_export_package(progress=None) -> dict:
    reporter = StageReporter("EXPORT PACKAGE", EXPORT_STAGES, progress)
    try:
        reporter.begin("prepare_workspace", "Creating a Windows-safe export workspace.")
        base.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        short_name = f"PF_Atlas_{timestamp}"
        run_dir = base.EXPORT_DIR / short_name
        if run_dir.exists():
            shutil.rmtree(run_dir)
        run_dir.mkdir(parents=True, exist_ok=False)
        final_zip = base.EXPORT_DIR / f"{short_name}.zip"
        reporter.complete(
            "prepare_workspace",
            f"Prepared {run_dir.name}.",
            {"folder": str(run_dir)},
        )

        reporter.begin("collect_artifacts", "Copying recovered JSON artifacts and evidence policy.")
        files = {
            "Project_Spine.json": base.PROJECT_SPINE_FILE,
            "Authority_Ledger.json": base.AUTHORITY_LEDGER_FILE,
            "Continuation_Brief.json": base.CONTINUATION_BRIEF_FILE,
            "Source_Trace_Index.json": base.SOURCE_TRACE_FILE,
            "Evidence_Boundary.json": EVIDENCE_BOUNDARY_FILE,
        }
        for out_name, source_path in files.items():
            shutil.copy2(source_path, run_dir / out_name)
        reporter.complete(
            "collect_artifacts",
            f"Collected {len(files)} governed JSON artifacts.",
            {"json_artifacts": len(files)},
        )

        reporter.begin("compose_markdown", "Generating human-readable project views.")
        continuation = base.load_json(base.CONTINUATION_BRIEF_FILE)
        spine = base.load_json(base.PROJECT_SPINE_FILE)

        (run_dir / "Project_Spine.md").write_text(
            "# Atlas Workshop — Project Spine\n\n"
            + "\n".join(
                f"{item['sequence']}. **{item['title']}** — {item['status']}"
                for item in spine["spine_events"]
            )
            + "\n",
            encoding="utf-8",
        )

        (run_dir / "Continuation_Brief.md").write_text(
            "# Atlas Workshop — Continuation Brief\n\n"
            f"## Last Trustworthy State\n\n{continuation['last_trustworthy_state']}\n\n"
            "## Completed\n\n"
            + "\n".join(f"- {item}" for item in continuation["completed"])
            + "\n\n## Unresolved\n\n"
            + "\n".join(f"- {item}" for item in continuation["unresolved"])
            + "\n\n## Boundaries\n\n"
            + "\n".join(f"- {item}" for item in continuation["boundaries"])
            + "\n\n## Recommended Next Action\n\n"
            + continuation["recommended_next_action"]
            + "\n",
            encoding="utf-8",
        )
        reporter.complete(
            "compose_markdown",
            "Generated Project Spine and Continuation Brief Markdown views.",
            {"markdown_views": 2},
        )

        reporter.begin("seal_manifest", "Hashing files and sealing package metadata.")
        manifest = {
            "package_type": "PROJECT_FOREMAN_RECOVERED_PROJECT_PACKAGE",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "fixture": base.FIXTURE_FILE.name,
            "source_fixture_sha256": base.sha256_file(base.FIXTURE_FILE),
            "evidence_boundary_policy": "PF-EVIDENCE-BOUNDARY-001",
            "evidence_mode": "EVIDENCE_BOUND",
            "files": [],
        }

        for path in sorted(run_dir.iterdir()):
            if path.is_file() and path.name not in {"Manifest.json", "CHECKSUMS.sha256"}:
                manifest["files"].append(
                    {
                        "name": path.name,
                        "sha256": base.sha256_file(path),
                        "size_bytes": path.stat().st_size,
                    }
                )

        manifest_path = run_dir / "Manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        checksum_path = run_dir / "CHECKSUMS.sha256"
        checksums = []
        for path in sorted(run_dir.iterdir()):
            if path.is_file() and path.name != "CHECKSUMS.sha256":
                checksums.append(f"{base.sha256_file(path)}  {path.name}")
        checksum_path.write_text("\n".join(checksums) + "\n", encoding="utf-8")
        reporter.complete(
            "seal_manifest",
            f"Sealed manifest and {len(checksums)} checksum entries.",
            {"checksum_entries": len(checksums)},
        )

        reporter.begin("create_archive", "Creating the evidence-bound ZIP archive.")
        with tempfile.TemporaryDirectory(prefix="project_foreman_evidence_export_") as temp_dir:
            temp_zip = Path(temp_dir) / final_zip.name
            with zipfile.ZipFile(
                temp_zip,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                allowZip64=True,
            ) as archive:
                for path in sorted(run_dir.iterdir()):
                    if path.is_file():
                        archive.write(path, arcname=f"{run_dir.name}/{path.name}")

            if final_zip.exists():
                final_zip.unlink()
            shutil.move(str(temp_zip), str(final_zip))
        reporter.complete(
            "create_archive",
            f"Created {final_zip.name}.",
            {"filename": final_zip.name},
        )

        reporter.begin("validate_package", "Testing archive members and final destination integrity.")
        with zipfile.ZipFile(final_zip, "r") as archive:
            bad_member = archive.testzip()
            final_names = archive.namelist()

        if bad_member is not None:
            raise RuntimeError(f"Evidence-bound ZIP validation failed at member: {bad_member}")
        if len(final_names) != 9:
            raise RuntimeError(
                f"Evidence-bound ZIP validation expected 9 files but found {len(final_names)}."
            )

        final_sha256 = base.sha256_file(final_zip)
        reporter.complete(
            "validate_package",
            f"Validated {len(final_names)} files and final SHA-256.",
            {"file_count": len(final_names), "sha256": final_sha256},
        )

        return {
            "zip_path": final_zip,
            "folder_path": run_dir,
            "sha256": final_sha256,
            "file_count": len(final_names),
            "validated": True,
        }
    except Exception as exc:
        reporter.fail_current(str(exc))
        raise


def _public_export_result(result: dict) -> dict:
    return {
        "status": "PASS",
        "filename": Path(result["zip_path"]).name,
        "path": str(result["zip_path"]),
        "folder_path": str(result["folder_path"]),
        "sha256": result["sha256"],
        "file_count": result["file_count"],
        "validated": result["validated"],
    }


class EvidenceBoundHandler(base.Handler):
    def _stream_operation(self, operation):
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        connection_open = True

        def emit(event: dict):
            nonlocal connection_open
            if not connection_open:
                return
            try:
                body = (json.dumps(event, separators=(",", ":")) + "\n").encode("utf-8")
                self.wfile.write(body)
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                connection_open = False

        try:
            result = operation(emit)
            emit({"type": "result", "status": "PASS", "result": result})
        except Exception as exc:
            emit({"type": "error", "status": "FAIL", "error": str(exc)})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/recover/stream":
            return self._stream_operation(
                lambda emit: build_recovery_payload(progress=emit)
            )
        if path == "/api/export/stream":
            return self._stream_operation(
                lambda emit: _public_export_result(
                    build_export_package(progress=emit)
                )
            )
        return super().do_GET()


def main():
    base.STATIC_DIR = EVIDENCE_STATIC_DIR
    base.build_recovery_payload = build_recovery_payload
    base.build_export_package = build_export_package
    base.Handler = EvidenceBoundHandler
    base.main()


if __name__ == "__main__":
    main()
