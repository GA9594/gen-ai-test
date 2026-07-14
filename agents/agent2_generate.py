"""
Agent 2 -- Generate.

Reads Agent 1's analysis and produces a dummy "artifact" (stands in for a code
patch, a generated file, a PR body, etc.). Chains via the analysis.json artifact.
"""
from __future__ import annotations

from common import (
    emit_notification,
    now_iso,
    read_artifact,
    write_artifact,
)

STEP_ID = "2"
TOOL_NAME = "generate"


def main() -> None:
    analysis = read_artifact("analysis")
    session_id = analysis["correlation_id"]

    emit_notification(
        session_id=session_id,
        tool_name=TOOL_NAME,
        step_id=STEP_ID,
        status="in_progress",
        msg_id=0,
        message="Generating artifact from analysis",
    )

    # ---- dummy generation logic -----------------------------------------
    keywords = analysis.get("derived_keywords", [])
    generated = {
        "correlation_id": session_id,
        "artifact_type": "patch",
        "content": "\n".join(f"# addressed: {kw}" for kw in keywords) or "# no-op patch",
        "lines_changed": len(keywords),
        "generated_at": now_iso(),
    }
    write_artifact("generation", generated)

    emit_notification(
        session_id=session_id,
        tool_name=TOOL_NAME,
        step_id=STEP_ID,
        status="completed",
        msg_id=0,
        success_code="A2-OK",
        message=f"Generated patch with {generated['lines_changed']} change(s)",
    )


if __name__ == "__main__":
    main()
