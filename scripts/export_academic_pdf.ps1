param(
    [string]$DocumentPath = 'output/documents/INFORME_ACADEMICO_FINAL.docx',
    [string]$PdfPath = 'output/pdf/INFORME_ACADEMICO_FINAL.pdf'
)
$ErrorActionPreference = 'Stop'
$taskDocument = (Resolve-Path -LiteralPath $DocumentPath).Path
$taskPdf = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $PdfPath))
$taskWord = $null
$taskDoc = $null
try {
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskWord.AutomationSecurity = 3
    $taskDoc = $taskWord.Documents.Open($taskDocument, $false, $false, $false)
    $taskDoc.Fields.Update() | Out-Null
    $taskDoc.Repaginate()
    $taskDoc.Save()
    $taskDoc.ExportAsFixedFormat($taskPdf, 17)
    Write-Output "PDF exported; pages=$($taskDoc.ComputeStatistics(2)); path=$taskPdf"
} finally {
    if ($null -ne $taskDoc) { $taskDoc.Close(0); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($taskDoc) | Out-Null }
    if ($null -ne $taskWord) { $taskWord.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($taskWord) | Out-Null }
}

