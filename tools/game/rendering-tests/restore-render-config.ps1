param([switch]$WhatIf)

$ConfigDir = "$env:LOCALAPPDATA\AcrGame\Saved\Config\WindowsNoEditor"
$BackupDir = "$env:LOCALAPPDATA\AcrGame\Saved\Config\WindowsNoEditor\G5_Backup"

Write-Host "=== G5 Config Restore ==="

if (-not (Test-Path $BackupDir)) {
    Write-Host "No backup found at $BackupDir"
    exit 1
}

$files = @("Engine.ini.bak", "GameUserSettings.ini.bak", "Scalability.ini.bak")
foreach ($f in $files) {
    $src = Join-Path $BackupDir $f
    $dst = Join-Path $ConfigDir ($f -replace "\.bak$", "")
    if (Test-Path $src) {
        if ($WhatIf) {
            Write-Host "[WhatIf] Would restore $dst from $src"
        } else {
            Copy-Item $src $dst -Force
            Write-Host "Restored: $dst"
        }
    }
}
Write-Host "Done"
