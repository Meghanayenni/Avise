$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

.venv\Scripts\python.exe -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

.venv\Scripts\python.exe -m tools.seed
