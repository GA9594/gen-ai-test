"""
Callback step -- the "ZAS_TASK_END" side of the contract.

Runs after the agent chain finishes (success OR failure). It reads the final
result.json (if present), builds the END envelope, and POSTs it to the broker's
/callbacks/complete endpoint. The correlation_id lets the broker match this back
to the original handoff and notify the ZAS Orchestrator.

Uses only the standard library so it runs on a bare GitHub runner with no pip
install step.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from common import TASK_END_MARKER, WORK_DIR, now_iso


def build_envelope() -> dict:
    task = json.loads(os.environ.get("ZAS_TASK_ENVELOPE", "{}"))
    correlation_id = task.get("correlation_id") or os.environ.get("ZAS_CORRELATION_ID", "")

    result_path = WORK_DIR / "result.json"
    if result_path.exists():
        result = json.loads(result_path.read_text())
        status = result.get("status", "COMPLETED")
    else:
        # The chain died before Agent 3 wrote a result.
        result = {"error": "no result artifact produced"}
        status = "FAILED"

    return {
        "zas_marker": TASK_END_MARKER,
        "correlation_id": correlation_id,
        "status": status,
        "result": result,
        "github": {
            "repository": os.environ.get("GITHUB_REPOSITORY", ""),
            "run_id": os.environ.get("GITHUB_RUN_ID", ""),
            "run_url": (
                f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/"
                f"{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/"
                f"{os.environ.get('GITHUB_RUN_ID', '')}"
            ),
        },
        "completed_at": now_iso(),
    }


def main() -> None:
    envelope = build_envelope()
    task = json.loads(os.environ.get("ZAS_TASK_ENVELOPE", "{}"))
    callback_url = task.get("callback_url") or os.environ.get("ZAS_CALLBACK_URL", "")

    body = json.dumps(envelope).encode()
    print(f"[CALLBACK] posting {TASK_END_MARKER} for "
          f"correlation_id={envelope['correlation_id']} status={envelope['status']}")
    print(f"[CALLBACK] -> {callback_url}")

    if not callback_url:
        print("[CALLBACK] no callback_url configured; printing envelope only:")
        print(json.dumps(envelope, indent=2))
        return

    req = urllib.request.Request(
        callback_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    token = os.environ.get("ZAS_CALLBACK_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"[CALLBACK] broker responded {resp.status}: {resp.read().decode()[:500]}")
    except urllib.error.HTTPError as e:
        print(f"[CALLBACK] broker HTTP error {e.code}: {e.read().decode()[:500]}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[CALLBACK] could not reach broker: {e.reason}")
        sys.exit(1)


if __name__ == "__main__":
    main()
