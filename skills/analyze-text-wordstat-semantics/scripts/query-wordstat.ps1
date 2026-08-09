[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateCount(3, 15)]
    [string[]]$Phrases,

    [ValidatePattern('^[a-z0-9]{20}$')]
    [string]$FolderId = 'b1gmbvaclm2pmt46cfnm',

    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Net.Http
$endpoint = 'https://searchapi.api.cloud.yandex.net/v2/wordstat/topRequests'
$apiKey = [Environment]::GetEnvironmentVariable('YANDEX_API_KEY', 'Process')
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    $apiKey = [Environment]::GetEnvironmentVariable('YANDEX_API_KEY', 'User')
}

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    throw 'NEEDS_API_KEY: set YANDEX_API_KEY in the current process or as a Windows User environment variable. Never pass the key as a script argument.'
}

$cleanPhrases = @($Phrases | ForEach-Object { $_.Trim() } | Where-Object { $_ } | Select-Object -Unique)
if ($cleanPhrases.Count -lt 3 -or $cleanPhrases.Count -gt 15) {
    throw 'Provide from 3 to 15 unique non-empty phrases.'
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $OutputPath = "D:\CODEX\outputs\wordstat-semantics-$stamp.json"
}

$resolvedOutput = [IO.Path]::GetFullPath($OutputPath)
$allowedRoot = [IO.Path]::GetFullPath('D:\CODEX\outputs') + [IO.Path]::DirectorySeparatorChar
if (-not $resolvedOutput.StartsWith($allowedRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'OutputPath must be inside D:\CODEX\outputs.'
}

$outputDirectory = Split-Path -Parent $resolvedOutput
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

$client = [Net.Http.HttpClient]::new()
$client.Timeout = [TimeSpan]::FromSeconds(45)
$client.DefaultRequestHeaders.Authorization = [Net.Http.Headers.AuthenticationHeaderValue]::new('Api-Key', $apiKey)
$records = [Collections.Generic.List[object]]::new()

try {
    foreach ($phrase in $cleanPhrases) {
        $payload = @{ phrase = $phrase; numPhrases = 100; folderId = $FolderId } | ConvertTo-Json -Compress
        $content = [Net.Http.StringContent]::new($payload, [Text.Encoding]::UTF8, 'application/json')
        try {
            try {
                $response = $client.PostAsync($endpoint, $content).GetAwaiter().GetResult()
            }
            catch [Net.Http.HttpRequestException] {
                throw 'WORDSTAT_NETWORK_ERROR: HTTPS connection to the official Wordstat API failed before an HTTP response was received. Do not rotate the API key. Run scripts/test-wordstat-network.ps1 and check VPN routing, TCP/443, and stale WinHTTP proxy settings.'
            }
            $bytes = $response.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()
            $responseText = [Text.Encoding]::UTF8.GetString($bytes)
            if (-not $response.IsSuccessStatusCode) {
                $status = [int]$response.StatusCode
                throw "Wordstat request failed with HTTP $status. Check access role, API-key scope, quota, billing, and request parameters."
            }
            $data = $responseText | ConvertFrom-Json
            $records.Add([pscustomobject]@{
                checkedQuery = $phrase
                totalCount = [long]$data.totalCount
                results = @($data.results)
                associations = @($data.associations)
            })
        }
        finally {
            $content.Dispose()
        }
    }
}
finally {
    $client.Dispose()
    $apiKey = $null
}

$result = [pscustomobject]@{
    source = $endpoint
    checkedAt = (Get-Date).ToString('o')
    period = 'last_30_days'
    regions = 'all'
    devices = 'all'
    folderId = $FolderId
    requestCount = $records.Count
    queries = $records
}

$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resolvedOutput -Encoding UTF8
Write-Output $resolvedOutput
