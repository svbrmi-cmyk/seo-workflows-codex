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
    $namespace = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    $sharedStrings = @()
    $sharedEntry = $archive.GetEntry('xl/sharedStrings.xml')

    if ($null -ne $sharedEntry) {
        $reader = [System.IO.StreamReader]::new($sharedEntry.Open(), [System.Text.Encoding]::UTF8)
        try {
            [xml]$sharedXml = $reader.ReadToEnd()
        }
        finally {
            $reader.Dispose()
        }

        $sharedNs = [System.Xml.XmlNamespaceManager]::new($sharedXml.NameTable)
        $sharedNs.AddNamespace('x', $namespace)

        foreach ($item in $sharedXml.SelectNodes('//x:si', $sharedNs)) {
            $parts = $item.SelectNodes('.//x:t', $sharedNs) |
                ForEach-Object { $_.InnerText }
            $sharedStrings += ($parts -join '')
        }
    }

    $sheetNameByTarget = @{}
    $workbookEntry = $archive.GetEntry('xl/workbook.xml')
    $relationsEntry = $archive.GetEntry('xl/_rels/workbook.xml.rels')

    if ($null -ne $workbookEntry -and $null -ne $relationsEntry) {
        $reader = [System.IO.StreamReader]::new($workbookEntry.Open(), [System.Text.Encoding]::UTF8)
        try {
            [xml]$workbookXml = $reader.ReadToEnd()
        }
        finally {
            $reader.Dispose()
        }

        $reader = [System.IO.StreamReader]::new($relationsEntry.Open(), [System.Text.Encoding]::UTF8)
        try {
            [xml]$relationsXml = $reader.ReadToEnd()
        }
        finally {
            $reader.Dispose()
        }

        $workbookNs = [System.Xml.XmlNamespaceManager]::new($workbookXml.NameTable)
        $workbookNs.AddNamespace('x', $namespace)
        $workbookNs.AddNamespace(
            'r',
            'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        )

        $targetByRelation = @{}
        foreach ($relation in $relationsXml.Relationships.Relationship) {
            $targetByRelation[$relation.Id] = $relation.Target
        }

        foreach ($sheet in $workbookXml.SelectNodes('//x:sheets/x:sheet', $workbookNs)) {
            $relationId = $sheet.GetAttribute(
                'id',
                'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
            )
            if ($targetByRelation.ContainsKey($relationId)) {
                $targetName = [System.IO.Path]::GetFileName($targetByRelation[$relationId])
                $sheetNameByTarget[$targetName] = $sheet.name
            }
        }
    }

    Write-Output ('FILE ' + [System.IO.Path]::GetFileName($resolvedPath))

    $worksheets = $archive.Entries |
        Where-Object { $_.FullName -match '^xl/worksheets/sheet\d+\.xml$' } |
        Sort-Object FullName

    foreach ($entry in $worksheets) {
        $targetName = [System.IO.Path]::GetFileName($entry.FullName)
        $sheetName = if ($sheetNameByTarget.ContainsKey($targetName)) {
            $sheetNameByTarget[$targetName]
        }
        else {
            $entry.FullName
        }

        $reader = [System.IO.StreamReader]::new($entry.Open(), [System.Text.Encoding]::UTF8)
        try {
            [xml]$sheetXml = $reader.ReadToEnd()
        }
        finally {
            $reader.Dispose()
        }

        $sheetNs = [System.Xml.XmlNamespaceManager]::new($sheetXml.NameTable)
        $sheetNs.AddNamespace('x', $namespace)
        Write-Output ('SHEET ' + $sheetName + ' (' + $entry.FullName + ')')

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
