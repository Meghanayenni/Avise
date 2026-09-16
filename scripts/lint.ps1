$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

.venv\Scripts\python.exe -m ruff check avise tools tests
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

.venv\Scripts\python.exe -m mypy avise
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (Test-Path "web\package.json") {
    Push-Location web
    npm run typecheck
    $code = $LASTEXITCODE
    Pop-Location
    if ($code -ne 0) { exit $code }
}
