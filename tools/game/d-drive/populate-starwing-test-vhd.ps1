# populate-starwing-test-vhd.ps1 — Copies D DRIVE CONTENTS to mounted D: drive
# Safety: $ErrorActionPreference = "Stop", only copies from source to D:
$ErrorActionPreference = "Stop"

$SourceRoot = "X:\StarwingParadox\D DRIVE CONTENTS"
$TargetRoot = "D:\"

# Verify source exists
if (-not (Test-Path $SourceRoot)) {
    Write-Error "Source not found: $SourceRoot"
    exit 1
}

# Verify D: exists and is writable
if (-not (Test-Path "D:\")) {
    Write-Error "D: drive not mounted. Run mount-starwing-test-vhd.ps1 first."
    exit 1
}

Write-Host "Populating D: drive from $SourceRoot..."

# Create required directory structure
$dirs = @(
    "D:\Saved\ACRSaved\SaveData",
    "D:\Saved\ACRSaved\Ranking",
    "D:\Saved\ACRSaved\SendLog",
    "D:\Saved\ACRSaved\Debug",
    "D:\Saved\ACRSaved\TestMode\BookKeeping\Old",
    "D:\Saved\ACRSaved\TestMode\Game",
    "D:\Saved\ACRSaved\TestMode\NesicaTime",
    "D:\Saved\ACRSaved\TestMode\OnePlayFree",
    "D:\Saved\ACRSaved\TestMode\Setting",
    "D:\Saved\ACRSaved\TestMode\Sound",
    "D:\Saved\ACRSaved\TestMode\Stick",
    "D:\Saved\ACRSaved\TestMode\System",
    "D:\Saved\GalaxySaved\AcrGame\Saved\Config\CrashReportClient",
    "D:\Saved\GalaxySaved\AcrGame\Saved\Config\WindowsNoEditor",
    "D:\Saved\GalaxySaved\AcrGame\Saved\Logs",
    "D:\Saved\GalaxySaved\AcrGame\Saved\SaveGames",
    "D:\Saved\GalaxySaved\UnrealEngine\4.16\Saved\Config\WindowsNoEditor",
    "D:\system\CmdFile\log",
    "D:\system\DUA\data",
    "D:\system\DUA\decrypt",
    "D:\system\DUA\download",
    "D:\system\DUA\event",
    "D:\system\DUA\news",
    "D:\system\DUA\unpack",
    "D:\system\DUA\work",
    "D:\system\Service"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Copy all files from source
$sourceFiles = Get-ChildItem $SourceRoot -Recurse -File -ErrorAction SilentlyContinue
$copied = 0
$failed = 0

foreach ($file in $sourceFiles) {
    $relativePath = $file.FullName.Substring($SourceRoot.Length + 1)
    $targetPath = Join-Path $TargetRoot $relativePath
    
    try {
        $targetDir = Split-Path $targetPath -Parent
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Copy-Item -Path $file.FullName -Destination $targetPath -Force
        $copied++
    } catch {
        Write-Warning "Failed to copy $relativePath : $_"
        $failed++
    }
}

Write-Host "`n=== Copy Summary ==="
Write-Host "Files copied: $copied"
Write-Host "Files failed: $failed"

# Verify key files exist
$keyFiles = @(
    "D:\Saved\ACRSaved\SaveData\OpenKey.json",
    "D:\Saved\ACRSaved\SaveData\SaveData.json",
    "D:\Saved\ACRSaved\Ranking\RankingData.json",
    "D:\Saved\ACRSaved\TestMode\Setting\test_mode_setting.json",
    "D:\system\option.txt"
)

Write-Host "`n=== Key File Verification ==="
foreach ($f in $keyFiles) {
    $exists = Test-Path $f
    $size = if ($exists) { (Get-Item $f).Length } else { 0 }
    Write-Host "$f : exists=$exists size=$size"
}

Write-Host "`nD: drive populated successfully"
