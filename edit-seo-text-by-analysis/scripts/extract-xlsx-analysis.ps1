param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

$ErrorActionPreference = 'Stop'
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$resolvedPath = (Resolve-Path -LiteralPath $Path).Path
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead($resolvedPath)

try {
    $sharedStrings = @()
    $sharedEntry = $archive.GetEntry('xl/sharedStrings.xml')

    if ($null -ne $sharedEntry) {
        $reader = [System.IO.StreamReader]::new($sharedEntry.Open())
        try {
            [xml]$sharedXml = $reader.ReadToEnd()
        }
        finally {
            $reader.Dispose()
        }

        $sharedNs = [System.Xml.XmlNamespaceManager]::new($sharedXml.NameTable)
        $sharedNs.AddNamespace('x', 'http://schemas.openxmlformats.org/spreadsheetml/2006/main')

        foreach ($item in $sharedXml.SelectNodes('//x:si', $sharedNs)) {
            $parts = $item.SelectNodes('.//x:t', $sharedNs) |
                ForEach-Object { $_.InnerText }
            $sharedStrings += ($parts -join '')
        }
    }

    Write-Output ('FILE ' + [System.IO.Path]::GetFileName($resolvedPath))

    $worksheets = $archive.Entries |
        Where-Object { $_.FullName -match '^xl/worksheets/sheet\d+\.xml$' } |
        Sort-Object FullName

    foreach ($entry in $worksheets) {
        $reader = [System.IO.StreamReader]::new($entry.Open())
        try {
            [xml]$sheetXml = $reader.ReadToEnd()
        }
        finally {
            $reader.Dispose()
        }

        $sheetNs = [System.Xml.XmlNamespaceManager]::new($sheetXml.NameTable)
        $sheetNs.AddNamespace('x', 'http://schemas.openxmlformats.org/spreadsheetml/2006/main')
        Write-Output ('SHEET ' + $entry.FullName)

        foreach ($row in $sheetXml.SelectNodes('//x:sheetData/x:row', $sheetNs)) {
            $values = @()

            foreach ($cell in $row.SelectNodes('./x:c', $sheetNs)) {
                $valueNode = $cell.SelectSingleNode('./x:v', $sheetNs)

                if ($cell.t -eq 'inlineStr') {
                    $value = ($cell.SelectNodes('.//x:t', $sheetNs) |
                        ForEach-Object { $_.InnerText }) -join ''
                }
                elseif ($null -eq $valueNode) {
                    $value = ''
                }
                elseif ($cell.t -eq 's') {
                    $value = $sharedStrings[[int]$valueNode.InnerText]
                }
                else {
                    $value = $valueNode.InnerText
                }

                $values += ($cell.r + '=' + $value)
            }

            Write-Output ($values -join "`t")
        }
    }
}
finally {
    $archive.Dispose()
}
