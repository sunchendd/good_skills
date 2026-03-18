$ErrorActionPreference = "Stop"

Write-Host ">> npx skills update -g -y" -ForegroundColor Cyan
npx skills update -g -y

Write-Host "Open source skill update completed." -ForegroundColor Green
