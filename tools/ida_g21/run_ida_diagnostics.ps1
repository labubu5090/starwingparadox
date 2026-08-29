# G21 IDA offline diagnostics runner
# Sets process-local symbol env to a local-only project dir, runs idat.exe
# in autonomous batch mode with an explicit script + log, and records a full
# diagnostics envelope (command, exit code, env, hashes, timestamps).
param(
    [Parameter(Mandatory=$true)][string]$Target,
    [string]$Script = "C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\ida_diagnostics.py",
    [string]$IdaExe = "C:\Program Files\IDA Professional 9.3\idat.exe",
    [string]$SymbolsDir = "C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\symbols",
    [string]$RunName = "g21"
)

$ErrorActionPreference = "Stop"
$root = "C:\Users\KAHO\Pictures\Starwing\tools\ida_g21"
$logDir = Join-Path $root "logs"
$outDir = Join-Path $root "out"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$log = Join-Path $logDir ("{0}_{1}_idat.log" -f $RunName, $stamp)
$stdout = Join-Path $logDir ("{0}_{1}_stdout.txt" -f $RunName, $stamp)
$stderr = Join-Path $logDir ("{0}_{1}_stderr.txt" -f $RunName, $stamp)
$envelope = Join-Path $outDir ("{0}_envelope.json" -f $RunName)

# Process-local symbol environment (no srv*/symsrv*/http/https/UNC)
$env:_NT_SYMBOL_PATH = $SymbolsDir
$env:_NT_ALT_SYMBOL_PATH = $SymbolsDir

function Get-Sha256($p){ (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash }

$targetHash = Get-Sha256 $Target

# Build command (batch autonomous, explicit log, explicit script)
$argsList = @(
    "-A",
    "-L`"$log`"",
    "-S`"$Script`"",
    "`"$Target`""
)
$cmdline = ("& `"{0}`" {1}" -f $IdaExe, ($argsList -join " "))

$preRun = [System.Collections.Generic.List[object]]::new()
foreach($f in @($Target,$Script)){ if(Test-Path -LiteralPath $f){ $preRun.Add(@{file=$f;sha256=(Get-Sha256 $f)}) } }

$sw = [System.Diagnostics.Stopwatch]::StartNew()
$p = Start-Process -FilePath $IdaExe -ArgumentList $argsList -Wait -PassThru -NoNewWindow `
    -RedirectStandardOutput $stdout -RedirectStandardError $stderr
$sw.Stop()
$exitCode = $p.ExitCode

# Post-run observations
$postTargetHash = Get-Sha256 $Target
$dbPath = $null
$dbSize = 0
$idb = ($Target + ".i64")
$idt = ($Target + ".idt")
foreach($cand in @($idb,$idt)){
    if(Test-Path -LiteralPath $cand){ $dbPath = $cand; $dbSize = (Get-Item -LiteralPath $cand).Length; break }
}
# Also bundled-style id0/id1/id2/nam/til database (IDA9 split) if present
$splitDb = @{}
Get-ChildItem -LiteralPath (Split-Path $Target) -Filter ("{0}.*" -f (Split-Path $Target -Leaf)) -ErrorAction SilentlyContinue | ForEach-Object {
  if($_.Extension -in @(".id0",".id1",".id2",".nam",".til")){ $splitDb[$_.Extension] = $_.Length }
}

$logText = ""
if(Test-Path -LiteralPath $log){ $logText = (Get-Content -LiteralPath $log -Raw) }

$envelope_ = @{
    run_name = $RunName
    command = $cmdline
    working_directory = (Get-Location).Path
    ida_exe = $IdaExe
    target = $Target
    target_sha256_before = $targetHash
    target_sha256_after = $postTargetHash
    symbols_dir = $SymbolsDir
    effective = @{
        _NT_SYMBOL_PATH = $env:_NT_SYMBOL_PATH
        _NT_ALT_SYMBOL_PATH = $env:_NT_ALT_SYMBOL_PATH
    }
    process = @{
        exit_code = $exitCode
        elapsed_ms = $sw.ElapsedMilliseconds
        pid = $p.Id
    }
    db = @{ path = $dbPath; size = $dbSize; split_db = $splitDb }
    log_path = $log
    stdout_path = $stdout
    stderr_path = $stderr
    log_tail = ($logText -split "`r?`n" | Select-Object -Last 60) -join "`n"
    network_keywords = @()
    timestamp = $stamp
}
# Network/PDB keyword scan over full log text
foreach($kw in @("msdl","symbol server","symsrv","http://","https://","download","PDB lookup","Connection reset","timeout","remote path")){
    if($logText -match [regex]::Escape($kw)){ $envelope_.network_keywords += $kw }
}
$envelope_ | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $envelope -Encoding UTF8
Write-Output "ENVELOPE: $envelope"
Write-Output "EXIT: $exitCode"
