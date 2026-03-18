$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$sources = Join-Path $root "sources.txt"

if (-not (Test-Path $sources)) {
    throw "sources.txt not found: $sources"
}

$lines = Get-Content -Path $sources -Encoding UTF8

foreach ($line in $lines) {
    $command = $line.Trim()

    if (-not $command) {
        continue
    }

    if ($command.StartsWith("#")) {
        continue
    }

    Write-Host ">> $command" -ForegroundColor Cyan
    Invoke-Expression $command
}

Write-Host "Open source skill installation completed." -ForegroundColor Green
