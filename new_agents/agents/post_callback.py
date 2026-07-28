"""
Callback step -- send the final result back to the ZAS broker.

Reads result.json and POSTs it to the callback_url ZAS gave us. The
correlation_id is what lets the broker match this result back to the task it
handed off. Standard library only, so no pip install on the runner.
"""
import json
import os
import urllib.error
import urllib.request

WORK_DIR = os.environ.get("ZAS_WORK_DIR", ".zas_work")
correlation_id = os.environ["ZAS_CORRELATION_ID"]
callback_url = os.environ.get("ZAS_CALLBACK_URL", "")

result_path = f"{WORK_DIR}/result.json"
if os.path.exists(result_path):
    with open(result_path) as f:
        result = json.load(f)
    status = result.get("status", "COMPLETED")
else:
    result = {"error": "agents did not produce a result"}
    status = "FAILED"

payload = {
    "correlation_id": correlation_id,
    "status": status,
    "result": result,
    "github": {
        "repository": os.environ.get("GITHUB_REPOSITORY", ""),
        "run_id": os.environ.get("GITHUB_RUN_ID", ""),
    },
}

print(f"[CALLBACK] correlation_id = {correlation_id}")
print(f"[CALLBACK] status         = {status}")
print(f"[CALLBACK] posting to     = {callback_url or '(none configured)'}")
print("[CALLBACK] payload:")
print(json.dumps(payload, indent=2))

if not callback_url:
    print("[CALLBACK] no callback_url -- printed only")
    raise SystemExit(0)

req = urllib.request.Request(
    callback_url,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"[CALLBACK] broker replied {resp.status}: {resp.read().decode()[:300]}")
except urllib.error.HTTPError as e:
    print(f"[CALLBACK] broker HTTP error {e.code}: {e.read().decode()[:300]}")
    raise SystemExit(1)
except urllib.error.URLError as e:
    print(f"[CALLBACK] could not reach broker: {e.reason}")
    raise SystemExit(1)
