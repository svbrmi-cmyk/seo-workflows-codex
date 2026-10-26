# Operations

All commands run from the unpacked kit root in Windows PowerShell.

## Install or verify

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install.ps1
.\verify.ps1
```

`install.ps1` imports the workflow without credentials and installs this skill. It does not execute the workflow. After installation, open `http://localhost:5678`, create the required credentials, and select them in every credentialed node.

`verify.ps1` is a fresh-install check and expects zero credential bindings. After credentials are configured, use the skill status helper instead.

## Start or stop the server

```powershell
.\start.ps1
.\stop.ps1
```

These commands only change the Docker container lifecycle. They do not activate, publish, or execute the workflow.

## Read-only status

From the installed skill directory, Codex can run:

```powershell
.\scripts\status.ps1 -KitRoot "C:\path\to\polmix-n8n-codex-kit"
```

Report the returned safe JSON fields. Do not replace the helper with raw database or credential queries.

## Approved batch

Proceed only when the current user request explicitly authorizes generation after being told the external side effects. Then run:

```powershell
.\scripts\run-approved-batch.ps1 `
  -KitRoot "C:\path\to\polmix-n8n-codex-kit" `
  -Count 10 `
  -StartRow 12 `
  -Authorized
```

`StartRow` is an assertion about the next eligible sheet row, not a selector that bypasses the queue. Omit it when the next row number is unknown. The runner stops rather than processing an unexpected row.

If the run is interrupted, call `status.ps1`, inspect the last safe journal lines printed by the runner, and resume only the remaining bounded count. Never infer a new execution permission from the interrupted run.
