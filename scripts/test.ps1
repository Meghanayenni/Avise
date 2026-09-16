$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

.venv\Scripts\python.exe -m pytest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (Test-Path "web\package.json") {
    Push-Location web
    npm run typecheck
    $code = $LASTEXITCODE
    Pop-Location
    if ($code -ne 0) { exit $code }
}
