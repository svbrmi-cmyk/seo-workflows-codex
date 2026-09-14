[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$targetHost = 'searchapi.api.cloud.yandex.net'
$resolved = @(Resolve-DnsName $targetHost -Type A | Where-Object { $_.IPAddress } | Select-Object -ExpandProperty IPAddress -Unique)

if ($resolved.Count -eq 0) {
    throw "WORDSTAT_DNS_ERROR: no IPv4 address resolved for $targetHost."
}

$warnings = [Collections.Generic.List[string]]::new()
try {
    $physical = @(Get-NetIPConfiguration -ErrorAction Stop | Where-Object {
        $_.IPv4DefaultGateway -and $_.IPv4Address -and $_.NetAdapter.Status -eq 'Up'
    } | ForEach-Object {
        [pscustomobject]@{
            interfaceIndex = $_.InterfaceIndex
            interfaceAlias = $_.InterfaceAlias
            ipv4 = $_.IPv4Address.IPAddress
            gateway = $_.IPv4DefaultGateway.NextHop
        }
    })
}
catch {
    $physical = @()
    $warnings.Add('Physical interface details are unavailable in the current security context. Run PowerShell as administrator to obtain interface index and gateway.')
}

$targets = foreach ($address in $resolved) {
    $tcp = Test-NetConnection $address -Port 443 -WarningAction SilentlyContinue
    try {
        $route = Find-NetRoute -RemoteIPAddress $address -ErrorAction Stop | Select-Object -First 1
    }
    catch {
        $route = $null
        $warnings.Add("Route details for $address are unavailable in the current security context.")
    }
    [pscustomobject]@{
        host = $targetHost
        ipv4 = $address
        tcp443 = $tcp.TcpTestSucceeded
        selectedInterface = $tcp.InterfaceAlias
        routeInterfaceIndex = $route.InterfaceIndex
        routeInterfaceAlias = $route.InterfaceAlias
        routeNextHop = $route.NextHop
        routePrefix = $route.DestinationPrefix
    }
}

$winHttpProxy = (netsh winhttp show proxy | Out-String).Trim()

[pscustomobject]@{
    checkedAt = (Get-Date).ToString('o')
    targets = @($targets)
    physicalInterfaces = @($physical)
    winHttpProxy = $winHttpProxy
    warnings = @($warnings)
    guidance = 'If only the API IP is captured by a failing VPN route, create an administrator-approved persistent /32 route through the measured physical gateway. Never disable VPN or firewall globally.'
} | ConvertTo-Json -Depth 6
