# One command back to a clean seeded state. This DESTROYS the local database volume.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

docker compose down -v
docker compose up -d db

Write-Host "Waiting for PostgreSQL..."
for ($i = 0; $i -lt 30; $i++) {
    docker compose exec -T db pg_isready -U avise *> $null
    if ($LASTEXITCODE -eq 0) { break }
    Start-Sleep -Seconds 1
}

if (Test-Path "uploads") { Remove-Item -Recurse -Force uploads }
New-Item -ItemType Directory -Path uploads | Out-Null

.venv\Scripts\python.exe -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

.venv\Scripts\python.exe -m tools.seed
