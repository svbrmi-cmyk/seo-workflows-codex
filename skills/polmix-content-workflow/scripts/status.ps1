param(
    [Parameter(Mandatory = $true)]
    [string]$KitRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ScriptDirectory = $PSScriptRoot
$InstallationFile = Join-Path $KitRoot '.installation/workflow.json'
$HelperFile = Join-Path $KitRoot 'tools/Get-PolmixWorkflow.ps1'

if (-not (Test-Path -LiteralPath $InstallationFile)) {
    throw 'Installation metadata is missing. Run install.ps1 from the kit root.'
}
if (-not (Test-Path -LiteralPath $HelperFile)) {
    throw 'Safe workflow helper is missing from the kit.'
}

. $HelperFile
$installation = Get-Content -LiteralPath $InstallationFile -Raw | ConvertFrom-Json
$workflow = Get-PolmixWorkflow -WorkflowId ([string]$installation.workflowId) -KitRoot $KitRoot
$contentRoot = Join-Path $KitRoot 'content/generated'
$markdownCount = @(Get-ChildItem -LiteralPath $contentRoot -File -Filter '*.md' -ErrorAction SilentlyContinue).Count
$researchCount = @(Get-ChildItem -LiteralPath $contentRoot -File -Filter '*.research.json' -ErrorAction SilentlyContinue).Count

[ordered]@{
    workflowId = $workflow.id
    name = $workflow.name
    active = $workflow.active
    activeVersionId = $workflow.activeVersionId
    isArchived = $workflow.isArchived
    nodeCount = $workflow.nodeCount
    credentialBindingCount = $workflow.credentialBindingCount
    markdownCount = $markdownCount
    researchCount = $researchCount
    credentialValuesRead = $false
} | ConvertTo-Json
