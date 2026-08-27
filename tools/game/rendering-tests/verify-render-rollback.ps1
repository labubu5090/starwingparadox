param([switch]$WhatIf)

$ConfigDir = "$env:LOCALAPPDATA\AcrGame\Saved\Config\WindowsNoEditor"
$BackupDir = "$env:LOCALAPPDATA\AcrGame\Saved\Config\WindowsNoEditor\G5_Backup"

Write-Host "=== G5 Config Rollback Verification ==="

$files = @("Engine.ini", "GameUserSettings.ini", "Scalability.ini")
$allOk = $true
foreach ($f in $files) {
    $current = Join-Path $ConfigDir $f
    $backup = Join-Path $BackupDir "$f.bak"
    if (Test-Path $backup) {
        $currentHash = if (Test-Path $current) { (Get-FileHash $current -Algorithm SHA256).Hash } else { "MISSING" }
        $backupHash = (Get-FileHash $backup -Algorithm SHA256).Hash
        $match = $currentHash -eq $backupHash
        Write-Host "$f : match=$match (current=$currentHash, backup=$backupHash)"
        if (-not $match) { $allOk = $false }
    }
}
if ($allOk) { Write-Host "VERIFICATION PASSED" } else { Write-Host "VERIFICATION FAILED" }
