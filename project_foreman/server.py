
from __future__ import annotations

import hashlib
import json
import os
import shutil
import threading
import webbrowser
import zipfile
import tempfile
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

PACKAGE_ROOT = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_ROOT / "data"
STATIC_DIR = PACKAGE_ROOT / "static"
EXPORT_DIR = Path.home() / "Downloads" / "Project_Foreman_Exports"

FIXTURE_FILE = DATA_DIR / "atlas_workshop_conversation.json"
PROJECT_SPINE_FILE = DATA_DIR / "Project_Spine.json"
AUTHORITY_LEDGER_FILE = DATA_DIR / "Authority_Ledger.json"
CONTINUATION_BRIEF_FILE = DATA_DIR / "Continuation_Brief.json"
SOURCE_TRACE_FILE = DATA_DIR / "Source_Trace_Index.json"

HOST = "127.0.0.1"
PORT = 8765


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_recovery_payload():
    fixture = load_json(FIXTURE_FILE)
    spine = load_json(PROJECT_SPINE_FILE)
    authority = load_json(AUTHORITY_LEDGER_FILE)
    continuation = load_json(CONTINUATION_BRIEF_FILE)
    trace = load_json(SOURCE_TRACE_FILE)

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
    }


def build_export_package() -> dict:
    """Create and validate a real export ZIP in a Windows-safe short path."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    short_name = f"PF_Atlas_{timestamp}"
    run_dir = EXPORT_DIR / short_name

    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=False)

    files = {
        "Project_Spine.json": PROJECT_SPINE_FILE,
        "Authority_Ledger.json": AUTHORITY_LEDGER_FILE,
        "Continuation_Brief.json": CONTINUATION_BRIEF_FILE,
        "Source_Trace_Index.json": SOURCE_TRACE_FILE,
    }

    for out_name, source_path in files.items():
        shutil.copy2(source_path, run_dir / out_name)

    continuation = load_json(CONTINUATION_BRIEF_FILE)
    spine = load_json(PROJECT_SPINE_FILE)

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
        + "\n".join(f"- {x}" for x in continuation["completed"])
        + "\n\n## Unresolved\n\n"
        + "\n".join(f"- {x}" for x in continuation["unresolved"])
        + "\n\n## Boundaries\n\n"
        + "\n".join(f"- {x}" for x in continuation["boundaries"])
        + "\n\n## Recommended Next Action\n\n"
        + continuation["recommended_next_action"]
        + "\n",
        encoding="utf-8",
    )

    manifest = {
        "package_type": "PROJECT_FOREMAN_RECOVERED_PROJECT_PACKAGE",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fixture": FIXTURE_FILE.name,
        "source_fixture_sha256": sha256_file(FIXTURE_FILE),
        "files": [],
    }

    for path in sorted(run_dir.iterdir()):
        if path.is_file():
            manifest["files"].append(
                {
                    "name": path.name,
                    "sha256": sha256_file(path),
                    "size_bytes": path.stat().st_size,
                }
            )

    (run_dir / "Manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    checksums = []
    for path in sorted(run_dir.iterdir()):
        if path.is_file() and path.name != "CHECKSUMS.sha256":
            checksums.append(f"{sha256_file(path)}  {path.name}")
    (run_dir / "CHECKSUMS.sha256").write_text(
        "\n".join(checksums) + "\n", encoding="utf-8"
    )

    final_zip = EXPORT_DIR / f"{short_name}.zip"

    # Build outside the synchronized destination, validate, then move atomically.
    with tempfile.TemporaryDirectory(prefix="project_foreman_export_") as temp_dir:
        temp_zip = Path(temp_dir) / f"{short_name}.zip"
        with zipfile.ZipFile(
            temp_zip,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=True,
        ) as zf:
            for path in sorted(run_dir.iterdir()):
                if path.is_file():
                    zf.write(path, arcname=f"{short_name}/{path.name}")

        with zipfile.ZipFile(temp_zip, "r") as zf:
            bad_member = zf.testzip()
            names = zf.namelist()

        if bad_member is not None:
            raise RuntimeError(f"ZIP validation failed at member: {bad_member}")
        if len(names) != 8:
            raise RuntimeError(
                f"ZIP validation expected 8 files but found {len(names)}."
            )

        if final_zip.exists():
            final_zip.unlink()
        shutil.move(str(temp_zip), str(final_zip))

    # Final destination validation after move.
    with zipfile.ZipFile(final_zip, "r") as zf:
        bad_member = zf.testzip()
        final_names = zf.namelist()

    if bad_member is not None:
        raise RuntimeError(
            f"Final ZIP validation failed at member: {bad_member}"
        )

    return {
        "zip_path": final_zip,
        "folder_path": run_dir,
        "sha256": sha256_file(final_zip),
        "file_count": len(final_names),
        "validated": True,
    }

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            return self._send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
        if path == "/app.js":
            return self._send_file(STATIC_DIR / "app.js", "application/javascript; charset=utf-8")
        if path == "/styles.css":
            return self._send_file(STATIC_DIR / "styles.css", "text/css; charset=utf-8")
        if path == "/api/fixture":
            fixture = load_json(FIXTURE_FILE)
            return self._send_json(fixture)
        if path == "/api/recover":
            return self._send_json(build_recovery_payload())
        if path == "/api/export":
            try:
                result = build_export_package()
                return self._send_json(
                    {
                        "status": "PASS",
                        "filename": result["zip_path"].name,
                        "path": str(result["zip_path"]),
                        "folder_path": str(result["folder_path"]),
                        "sha256": result["sha256"],
                        "file_count": result["file_count"],
                        "validated": result["validated"],
                    }
                )
            except Exception as exc:
                return self._send_json(
                    {
                        "status": "FAIL",
                        "error": str(exc),
                    },
                    status=500,
                )

        self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        return


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    print("\nPROJECT FOREMAN")
    print(f"Open: {url}")
    print("Press Ctrl+C to stop.\n")

    if os.environ.get("PROJECT_FOREMAN_NO_BROWSER") != "1":
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Project Foreman.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
