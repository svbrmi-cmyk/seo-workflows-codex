param(
    [string]$LibraryRoot = 'D:\CODEX\seo-workflows-codex',
    [string]$CodexSkillRoot = 'C:\Users\aleks\.codex\skills',
    [string]$WorkspaceSkillRoot = 'D:\CODEX\.agents\skills',
    [string]$BackupRoot = 'D:\CODEX\outputs\skill-consolidation-20261026\backups'
)
$ErrorActionPreference = 'Stop'
$canonicalRoot = (Resolve-Path -LiteralPath (Join-Path $LibraryRoot 'skills')).Path
if (-not $canonicalRoot.StartsWith('D:\CODEX\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Canonical skill storage must remain under D:\CODEX.'
}
if (-not ([IO.Path]::GetFullPath($BackupRoot)).StartsWith('D:\CODEX\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Backups must remain under D:\CODEX.'
}
$skillFolders = @(Get-ChildItem -LiteralPath $canonicalRoot -Directory | Where-Object {
    Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md')
})
New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
function Set-SkillJunction([string]$Path, [string]$Target, [string]$BackupGroup) {
    $allowedRoots = @([IO.Path]::GetFullPath($CodexSkillRoot), [IO.Path]::GetFullPath($WorkspaceSkillRoot))
    $absolutePath = [IO.Path]::GetFullPath($Path)
    if ([IO.Path]::GetDirectoryName($absolutePath) -notin $allowedRoots) {
        throw "Unexpected link destination: $absolutePath"
    }
    $item = Get-Item -LiteralPath $absolutePath -Force -ErrorAction SilentlyContinue
    if ($null -ne $item) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            if (@($item.Target) -contains $Target) { return }
            Remove-Item -LiteralPath $absolutePath -Force
        } else {
            $backup = Join-Path (Join-Path $BackupRoot $BackupGroup) $item.Name
            if (Test-Path -LiteralPath $backup) { throw "Backup already exists: $backup" }
            New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($backup)) -Force | Out-Null
            Move-Item -LiteralPath $absolutePath -Destination $backup
        }
    }
    New-Item -ItemType Junction -Path $absolutePath -Target $Target | Out-Null
}
$grsPluginPresent = Test-Path -LiteralPath 'C:\Users\aleks\.codex\plugins\cache\grsai-transfer\grsai-text-generator\0.1.0+codex.20260729084450\skills\use-grsai-text\SKILL.md'
foreach ($root in @($CodexSkillRoot, $WorkspaceSkillRoot)) {
    New-Item -ItemType Directory -Path $root -Force | Out-Null
    foreach ($skill in $skillFolders) {
        if ($root -eq $CodexSkillRoot -and $skill.Name -eq 'use-grsai-text' -and $grsPluginPresent) { continue }
        Set-SkillJunction (Join-Path $root $skill.Name) $skill.FullName $(if ($root -eq $CodexSkillRoot) { 'codex-user' } else { 'workspace' })
    }
}
# An obsolete broken link does not contain a skill and cannot be loaded.
$legacy = Join-Path $CodexSkillRoot 'edit-seo-text-by-analysis'
$item = Get-Item -LiteralPath $legacy -Force -ErrorAction SilentlyContinue
if ($null -ne $item -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -and -not (Test-Path -LiteralPath (Join-Path $legacy 'SKILL.md'))) {
    Remove-Item -LiteralPath $legacy -Force
}
# Keep one user-level discovery location for this already duplicated skill.
$duplicate = 'C:\Users\aleks\.agents\skills\product-card-descriptions'
if ((Test-Path -LiteralPath $duplicate) -and (Test-Path -LiteralPath (Join-Path $CodexSkillRoot 'product-card-descriptions\SKILL.md'))) {
    $item = Get-Item -LiteralPath $duplicate -Force
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        Remove-Item -LiteralPath $duplicate -Force
    } else {
        $backup = Join-Path $BackupRoot 'agents-user\product-card-descriptions'
        if (Test-Path -LiteralPath $backup) { throw 'Duplicate backup already exists.' }
        New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($backup)) -Force | Out-Null
        Move-Item -LiteralPath $duplicate -Destination $backup
    }
}
$broken = @()
foreach ($root in @($CodexSkillRoot, $WorkspaceSkillRoot)) {
    foreach ($skill in $skillFolders) {
        if ($root -eq $CodexSkillRoot -and $skill.Name -eq 'use-grsai-text' -and $grsPluginPresent) { continue }
        if (-not (Test-Path -LiteralPath (Join-Path (Join-Path $root $skill.Name) 'SKILL.md'))) {
            $broken += "$root\$($skill.Name)"
        }
    }
}
if ($broken.Count) { throw ('Broken links: ' + ($broken -join ', ')) }
Write-Output ("Installed {0} canonical skills; GRS plugin present: {1}" -f $skillFolders.Count, $grsPluginPresent)
