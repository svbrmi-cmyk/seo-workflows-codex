---
name: polmix-content-workflow
description: Use when installing, checking, diagnosing, or explicitly running the packaged local Polmix content workflow in n8n on Windows.
---

# Polmix Content Workflow

Operate the packaged local n8n workflow from the opened `polmix-n8n-codex-kit` folder.

Before any n8n action, read [references/workflow-contract.md](references/workflow-contract.md). For installation, status, credentials setup, approved runs, or recovery, also read [references/operations.md](references/operations.md).

Use `.installation/workflow.json` as the sole workflow locator. If it is absent, stop and direct the user to `install.ps1`; do not guess an ID or search unrelated workflows.

Status checks are read-only. A generation run requires explicit authorization in the current user request because it can call search and LLM APIs, update Google Sheets, and write the local filesystem. Never treat installation, credential setup, a prior run, or a request to inspect status as permission to execute.

Keep the workflow inactive and unpublished. Never read or export credential values, API keys, OAuth tokens, or `.env`.
