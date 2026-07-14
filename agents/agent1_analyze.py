"""
Agent 1 -- Analyze.

Consumes the raw task handed off by ZAS and produces a small "analysis" that
the downstream agents act on. In a real integration this is where an LLM /
LangGraph agent would do root-cause analysis, intent extraction, planning, etc.
Here we just derive a deterministic plan so the chain is verifiable.
"""
from __future__ import annotations

from common import (
    emit_notification,
    load_task,
    now_iso,
    write_artifact,
)

STEP_ID = "1"
TOOL_NAME = "analyze"


def main() -> None:
    task = load_task()
    session_id = task["correlation_id"]
    task_input = task.get("task_input", {})

    emit_notification(
        session_id=session_id,
        tool_name=TOOL_NAME,
        step_id=STEP_ID,
        status="in_progress",
        msg_id=0,
        message="Analyzing delegated task from ZAS",
    )

    # ---- dummy analysis logic -------------------------------------------
    summary = task_input.get("summary", "(no summary provided)")
    keywords = sorted({w.lower().strip(".,") for w in summary.split() if len(w) > 4})
    analysis = {
        "correlation_id": session_id,
        "task_type": task.get("task_type"),
        "summary": summary,
        "derived_keywords": keywords,
        "recommended_action": "generate-patch",
        "analyzed_at": now_iso(),
    }
    write_artifact("analysis", analysis)

    emit_notification(
        session_id=session_id,
        tool_name=TOOL_NAME,
        step_id=STEP_ID,
        status="completed",
        msg_id=0,
        success_code="A1-OK",
        message=f"Analysis complete: {len(keywords)} keyword(s), action=generate-patch",
    )


if __name__ == "__main__":
    main()
