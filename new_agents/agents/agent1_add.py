"""
Agent 1 -- Add two numbers.

Reads its inputs from plain environment variables (no envelope wrapper) that the
workflow sets from the payload ZAS sent. Writes its result to a small JSON file
so Agent 2 can pick it up.
"""
import json
import os

WORK_DIR = os.environ.get("ZAS_WORK_DIR", ".zas_work")

# Inputs handed to us by ZAS (via the workflow).
correlation_id = os.environ["ZAS_CORRELATION_ID"]
a = float(os.environ.get("ZAS_NUM_A", "0"))
b = float(os.environ.get("ZAS_NUM_B", "0"))

print(f"[AGENT-1] correlation_id = {correlation_id}")
print(f"[AGENT-1] adding {a} + {b}")

total = a + b

print(f"[AGENT-1] result = {total}")

# Hand the result to the next agent.
os.makedirs(WORK_DIR, exist_ok=True)
with open(f"{WORK_DIR}/step1.json", "w") as f:
    json.dump({"correlation_id": correlation_id, "a": a, "b": b, "sum": total}, f, indent=2)

print("[AGENT-1] wrote step1.json -- done")
