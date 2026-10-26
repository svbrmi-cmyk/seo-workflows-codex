# Workflow contract

## Scope

- Resolve the installed workflow only from `<kit-root>/.installation/workflow.json`.
- Require the exact workflow name stored by the kit installer.
- Do not inspect, change, run, activate, publish, archive, import, or export any other workflow.
- Keep the selected workflow inactive, unpublished, and unarchived before and after every operation.

## Secrets

- Never read or export credential values, API keys, OAuth tokens, passwords, `.env`, the credential database tables, or the n8n encryption key.
- Credential metadata may be limited to a binding count. Credential creation and selection happen in the n8n UI.
- Fresh installation has zero bindings. Generation is allowed only after all 20 required node bindings are configured.

## Execution boundary

Status, file counts, and workflow-state checks are read-only and need no run authorization.

A generation run requires explicit authorization in the current user request. State the side effects before running: search and LLM API calls, Google Sheets reads/writes, and local filesystem writes. WordPress and media operations are outside the runnable path.

Bound every batch to 1–50 rows and every row to at most five attempts. Stop on a repeated row, unexpected source row, missing artifact, missing Google Sheets write, state change, or retry-limit exhaustion.

## Successful row

Count a row only when all of these are true:

1. n8n records a successful, finished execution.
2. `Сохранить Markdown` ran.
3. `Сохранить research JSON` ran.
4. `Google Sheets — записать путь к тексту` ran.
5. Both local files exist and their row-prefixed names agree.
6. The sheet path equals `content/polmix/<markdown-file>`.

Report completed row count, current/last row, execution ID, and a concise error location. Do not print raw execution payloads.
