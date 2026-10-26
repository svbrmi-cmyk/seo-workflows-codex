param(
    [Parameter(Mandatory = $true)]
    [string]$KitRoot,

    [Parameter(Mandatory = $true)]
    [ValidateRange(1, 50)]
    [int]$Count,

    [ValidateRange(0, 100000)]
    [int]$StartRow = 0,

    [ValidateRange(1, 5)]
    [int]$MaxAttempts = 3,

    [switch]$Authorized
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ScriptDirectory = $PSScriptRoot

if (-not $Authorized) {
    throw 'Explicit current-turn authorization is required because this run has external side effects.'
}

$InstallationFile = Join-Path $KitRoot '.installation/workflow.json'
$HelperFile = Join-Path $KitRoot 'tools/Get-PolmixWorkflow.ps1'
$ServerRoot = Join-Path $KitRoot 'server'
$ComposeFile = Join-Path $ServerRoot 'compose.yaml'
$EnvFile = Join-Path $ServerRoot '.env'

if (-not (Test-Path -LiteralPath $InstallationFile)) {
    throw 'Installation metadata is missing. Run install.ps1 first.'
}

. $HelperFile
$installation = Get-Content -LiteralPath $InstallationFile -Raw | ConvertFrom-Json
$workflowId = [string]$installation.workflowId
$state = Get-PolmixWorkflow -WorkflowId $workflowId -KitRoot $KitRoot
if ($state.active -ne $false -or $null -ne $state.activeVersionId -or $state.isArchived -ne $false) {
    throw 'Workflow must remain inactive, unpublished, and unarchived.'
}
if ([int]$state.credentialBindingCount -ne 20) {
    throw "All 20 credential bindings must be configured before generation; found $($state.credentialBindingCount)."
}

$arguments = @(
    '--workflow-id=' + $workflowId,
    '--target=' + $Count,
    '--start-row=' + $StartRow,
    '--max-attempts=' + $MaxAttempts,
    '--expected-credentials=20'
)

& docker compose --project-name polmix-n8n --project-directory $ServerRoot `
    -f $ComposeFile --env-file $EnvFile exec -T n8n `
    node /opt/polmix-tools/run-approved-batch-safe.cjs @arguments
if ($LASTEXITCODE -ne 0) {
    throw 'The approved batch stopped before reaching its target. Review the safe runner output.'
}
