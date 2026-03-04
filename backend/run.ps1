param(
    [ValidateSet("runserver", "check", "migrate", "seed")]
    [string]$Action = "runserver",
    [string]$Address = "127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "[ERROR] .venv not found. First-time setup:" -ForegroundColor Red
    Write-Host "python -m venv .venv"
    Write-Host ".\.venv\Scripts\python.exe -m pip install -r requirements.txt"
    exit 1
}

if (-not (Test-Path (Join-Path $PSScriptRoot ".env"))) {
    Write-Host "[WARN] .env file missing. Copy from .env.example before full run." -ForegroundColor Yellow
}

switch ($Action) {
    "check" {
        & $venvPython manage.py check
        break
    }
    "migrate" {
        & $venvPython manage.py migrate
        break
    }
    "seed" {
        & $venvPython manage.py seed_aptitude_questions
        & $venvPython manage.py seed_coding_questions
        break
    }
    "runserver" {
        & $venvPython manage.py runserver $Address
        break
    }
}
