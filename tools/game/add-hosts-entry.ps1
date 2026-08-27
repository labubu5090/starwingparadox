# Add Starwing dev.starwing.jp -> 127.0.0.1 to hosts file
# REQUIRES ADMIN PRIVILEGES
# Run as Administrator

$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
$backupPath = "C:\Users\KAHO\Pictures\Starwing\config\hosts.backup"
$entry = "127.0.0.1    dev.starwing.jp"

Write-Host "=== Starwing Hosts Update ==="

# Verify no conflict
$current = Get-Content $hostsPath -Raw
if ($current -match "dev\.starwing\.jp") {
    Write-Host "ERROR: dev.starwing.jp already exists in hosts file!"
    Write-Host "Existing entries:"
    Get-Content $hostsPath | Select-String "dev.starwing"
    exit 1
}

# Backup
Copy-Item $hostsPath $backupPath -Force
Write-Host "Backup saved: $backupPath"

# Add entry
Add-Content -Path $hostsPath -Value "`n$entry" -Encoding ASCII
Write-Host "Added: $entry"

# Verify
Write-Host "`nVerification:"
Get-Content $hostsPath | Select-String "dev.starwing"

# Flush DNS
ipconfig /flushdns | Select-String "Successfully"

Write-Host "`nDone. Test with: nslookup dev.starwing.jp"
