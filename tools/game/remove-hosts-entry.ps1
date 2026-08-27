# Remove Starwing dev.starwing.jp from hosts file
# REQUIRES ADMIN PRIVILEGES
# Run as Administrator

$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"

Write-Host "=== Starwing Hosts Rollback ==="

# Remove the line containing dev.starwing.jp
$lines = Get-Content $hostsPath | Where-Object { $_ -notmatch "dev\.starwing\.jp" -and $_.Trim() -ne "" }
Set-Content -Path $hostsPath -Value ($lines -join "`n") -Encoding ASCII
Write-Host "Removed dev.starwing.jp entry"

# Flush DNS
ipconfig /flushdns | Select-String "Successfully"

# Verify
Write-Host "`nVerification:"
$remaining = Get-Content $hostsPath | Select-String "dev.starwing"
if ($remaining) {
    Write-Host "WARNING: Entry still present!"
} else {
    Write-Host "Entry removed successfully"
}

Write-Host "`nDone."
