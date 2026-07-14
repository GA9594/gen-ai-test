"""
Shared helpers for the ZAS-delegated GitHub agents.

These helpers keep every agent speaking the same language as ZAS:
  * they read the incoming task envelope handed off by the ZAS broker,
  * they emit ZAS-style notification payloads (session_id / msg_id / status ...),
  * they read/write the small JSON artifacts that chain one agent to the next.

Nothing here talks to a real LLM -- the agents are deliberately "dummy" so we
can prove the *plumbing* (handoff -> agent chain -> callback) end to end.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Directory where agents drop their JSON artifacts so the next agent can pick
# them up. On a GitHub runner this is the checkout workspace; locally it is
# whatever ZAS_WORK_DIR points at.
WORK_DIR = Path(os.environ.get("ZAS_WORK_DIR", ".zas_work"))

# The unique tags that bracket a delegated task as it crosses the ZAS<->GitHub
# boundary. The broker stamps START into the dispatch payload; the final
# callback carries END. correlation_id ties the two together.
TASK_START_MARKER = "ZAS_TASK_START"
TASK_END_MARKER = "ZAS_TASK_END"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_task() -> dict:
    """Load the task envelope handed off by ZAS.

    On a GitHub Actions runner the envelope arrives as JSON in the
    ZAS_TASK_ENVELOPE env var (populated from the repository_dispatch
    client_payload). Locally the simulator sets the same variable.
    """
    raw = os.environ.get("ZAS_TASK_ENVELOPE")
    if not raw:
        raise SystemExit("ZAS_TASK_ENVELOPE is not set -- nothing to work on")
    envelope = json.loads(raw)
    if envelope.get("zas_marker") != TASK_START_MARKER:
        raise SystemExit(
            f"envelope missing {TASK_START_MARKER} marker; got "
            f"{envelope.get('zas_marker')!r}"
        )
    return envelope


def read_artifact(name: str) -> dict:
    """Read an artifact produced by an earlier agent in the chain."""
    path = WORK_DIR / f"{name}.json"
    if not path.exists():
        raise SystemExit(f"expected artifact {path} not found")
    return json.loads(path.read_text())


def write_artifact(name: str, data: dict) -> Path:
    """Persist this agent's output for the next agent in the chain."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    path = WORK_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2))
    return path


def emit_notification(
    *,
    session_id: str,
    tool_name: str,
    step_id: str,
    status: str,
    msg_id: int = 0,
    success_code: str = "",
    failure_code: str = "",
    message: str = "",
) -> dict:
    """Emit a ZAS-format notification payload.

    Matches the structure defined in the ZAS Integration Guide:
      msg_id == 0 -> intermediate  (message_notification)
      msg_id == 1 -> final result  (message_response)
    On a real ZAS agent this would be streamed back over A2A; here we print it
    to stdout so it shows up in the GitHub Actions log and the local run.
    """
    payload = {
        "session_id": session_id,
        "tool_name": tool_name,
        "step_id": step_id,
        "success_code": success_code,
        "failure_code": failure_code,
        "status": status,
        "msg_id": msg_id,
    }
    if msg_id == 1:
        payload["message_response"] = message
    else:
        payload["message_notification"] = message

    # A recognizable prefix so the notifications are easy to grep in CI logs.
    print(f"[ZAS-NOTIFY] {json.dumps(payload)}", flush=True)
    return payload
