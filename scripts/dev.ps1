# Starts the API, and the frontend once web/ is scaffolded (Phase 0 step 12).
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$api = Start-Process -PassThru -NoNewWindow -FilePath ".venv\Scripts\python.exe" `
    -ArgumentList "-m", "uvicorn", "avise.api.app:app", "--reload", "--port", "8000", "--no-access-log"
try {
    if (Test-Path "web\package.json") {
        Push-Location web
        npm run dev
        Pop-Location
    }
    else {
        Write-Host "web/ is not scaffolded yet - running the API alone. Ctrl+C to stop."
        Wait-Process -Id $api.Id
    }
}
finally {
    if (-not $api.HasExited) { Stop-Process -Id $api.Id -Force }
}
