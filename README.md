# GitHub-side: ZAS-delegated agents workflow

This is the content that gets pushed to a branch of `zebratechnologies/gen-ai`.
It is the "GitHub agents workflow" that ZAS delegates work to.

```
.github/workflows/zas-agents-workflow.yml   trigger + agent chain + callback
agents/
  common.py            shared: envelope loading, ZAS-format notifications, artifacts
  agent1_analyze.py    Agent 1  (analyze the task)
  agent2_generate.py   Agent 2  (generate an artifact from the analysis)
  agent3_review.py     Agent 3  (review + produce the final result)
  post_callback.py     final step: POST ZAS_TASK_END back to the broker
```

## How it is triggered

The broker fires a GitHub `repository_dispatch`:

```
POST https://api.github.com/repos/zebratechnologies/gen-ai/dispatches
Authorization: Bearer <PAT>
{ "event_type": "zas-task", "client_payload": { <ZAS_TASK_START envelope> } }
```

`client_payload` IS the start envelope and is threaded to every agent via the
`ZAS_TASK_ENVELOPE` env var:

```json
{
  "zas_marker": "ZAS_TASK_START",
  "correlation_id": "<zas session id>",
  "task_type": "code-remediation",
  "task_input": { "summary": "..." },
  "callback_url": "http://<broker>/callbacks/complete"
}
```

You can also run it manually from the Actions tab (`workflow_dispatch`).

## What it returns

The final step posts the `ZAS_TASK_END` envelope to `callback_url`, carrying the
same `correlation_id` so the broker can match it back to the original handoff.

## Enabling the real trigger

`repository_dispatch` only fires for workflow files that exist on the repo's
**default branch**. To trigger a workflow living on a feature branch, either
merge the workflow file to the default branch first, or trigger with
`workflow_dispatch` targeting the branch. See `../docs/GO_LIVE.md`.
