"""
Agent 3 -- Review.

Reads Agent 2's generated artifact, "reviews" it, and produces the final result
for the whole GitHub-side workflow. Emits the msg_id == 1 final response and
writes result.json which the callback step ships back to ZAS.
"""
from __future__ import annotations

from common import (
    emit_notification,
    now_iso,
    read_artifact,
    write_artifact,
)

STEP_ID = "3"
TOOL_NAME = "review"


def main() -> None:
    generation = read_artifact("generation")
    session_id = generation["correlation_id"]

    emit_notification(
        session_id=session_id,
        tool_name=TOOL_NAME,
        step_id=STEP_ID,
        status="in_progress",
        msg_id=0,
        message="Reviewing generated artifact",
    )

    # ---- dummy review logic ---------------------------------------------
    lines_changed = generation.get("lines_changed", 0)
    approved = lines_changed > 0
    verdict = "approved" if approved else "changes-requested"

    result = {
        "correlation_id": session_id,
        "status": "COMPLETED" if approved else "FAILED",
        "verdict": verdict,
        "artifact_type": generation.get("artifact_type"),
        "lines_changed": lines_changed,
        "reviewed_at": now_iso(),
        "summary": (
            f"Workflow completed: patch {verdict} "
            f"({lines_changed} change(s))"
        ),
    }
    write_artifact("result", result)

    emit_notification(
        session_id=session_id,
        tool_name=TOOL_NAME,
        step_id=STEP_ID,
        status="completed" if approved else "failed",
        msg_id=1,  # final response for the whole GitHub-side workflow
        success_code="A3-OK" if approved else "",
        failure_code="" if approved else "A3-REJECT",
        message=result["summary"],
    )


if __name__ == "__main__":
    main()
