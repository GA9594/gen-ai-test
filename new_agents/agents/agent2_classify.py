"""
Agent 2 -- Classify the result from Agent 1.

Picks up step1.json, does a little extra work on the sum (square it, say whether
it is even or odd), and writes result.json which the callback step sends to ZAS.
"""
import json
import os

WORK_DIR = os.environ.get("ZAS_WORK_DIR", ".zas_work")

with open(f"{WORK_DIR}/step1.json") as f:
    step1 = json.load(f)

total = step1["sum"]
print(f"[AGENT-2] received sum = {total} from Agent 1")

squared = total ** 2
parity = "even" if int(total) % 2 == 0 else "odd"

print(f"[AGENT-2] squared  = {squared}")
print(f"[AGENT-2] parity   = {parity}")

result = {
    "correlation_id": step1["correlation_id"],
    "status": "COMPLETED",
    "inputs": {"a": step1["a"], "b": step1["b"]},
    "sum": total,
    "squared": squared,
    "parity": parity,
    "summary": f"{step1['a']} + {step1['b']} = {total} ({parity}), squared = {squared}",
}

with open(f"{WORK_DIR}/result.json", "w") as f:
    json.dump(result, f, indent=2)

print(f"[AGENT-2] {result['summary']}")
print("[AGENT-2] wrote result.json -- done")
