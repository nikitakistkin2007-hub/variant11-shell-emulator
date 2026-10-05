# Calls the emulator with every command line parameter (Windows).
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Main = Join-Path $Root "src/main.py"
$Vfs = Join-Path $Root "vfs_demo"
$Startup = Join-Path $Root "scripts/startup.txt"
$Missing = Join-Path $Root "scripts/missing.txt"
$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }

function Run-Emulator {
    Write-Host ""
    Write-Host ('$ main.py ' + ($args -join " "))
    & $Python $Main @args
    Write-Host "[exit code: $LASTEXITCODE]"
}

Write-Host "=== --help ==="
Run-Emulator --help

Write-Host ""
Write-Host "=== --vfs only: interactive mode (input from a pipe) ==="
"ls -l`ncd /tmp`nrm x`nexit" | & $Python $Main --vfs $Vfs
Write-Host "[exit code: $LASTEXITCODE]"

Write-Host ""
Write-Host "=== --vfs and --script ==="
Run-Emulator --vfs $Vfs --script $Startup
Run-Emulator --vfs . --script $Startup

Write-Host ""
Write-Host "=== Parameter errors ==="
Run-Emulator
Run-Emulator --script $Startup
Run-Emulator --vfs $Vfs --script $Missing
Run-Emulator --vfs $Vfs --unknown
