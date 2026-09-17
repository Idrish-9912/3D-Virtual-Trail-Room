# Starts the React 3D room and its FastAPI/PostgreSQL backend together.
# Run from PowerShell: .\start-virtual-room.ps1

$ErrorActionPreference = 'Stop'

$rootDir = $PSScriptRoot
$backendDir = Join-Path $rootDir '3D-Backend\project'
$frontendDir = Join-Path $rootDir '3D-Frontend\project1'
$pythonExe = Join-Path $backendDir 'venv\Scripts\python.exe'
$logDir = Join-Path $rootDir 'logs'

function Test-PortOpen([int]$Port) {
    return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

foreach ($path in @($backendDir, $frontendDir, $pythonExe)) {
    if (-not (Test-Path $path)) {
        throw "Required project file was not found: $path"
    }
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

if (-not (Test-PortOpen 5432)) {
    throw 'PostgreSQL is not running on port 5432. Start the PostgreSQL service, then run this script again.'
}

if (-not (Test-PortOpen 8000)) {
    Start-Process -FilePath $pythonExe `
        -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000' `
        -WorkingDirectory $backendDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logDir 'backend.log') `
        -RedirectStandardError (Join-Path $logDir 'backend-error.log')
}

if (-not (Test-PortOpen 5173)) {
    Start-Process -FilePath 'npm.cmd' `
        -ArgumentList 'run', 'dev', '--', '--host', '127.0.0.1' `
        -WorkingDirectory $frontendDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logDir 'frontend.log') `
        -RedirectStandardError (Join-Path $logDir 'frontend-error.log')
}

for ($attempt = 1; $attempt -le 15; $attempt++) {
    if ((Test-PortOpen 8000) -and (Test-PortOpen 5173)) {
        Write-Host 'Virtual room is ready: http://127.0.0.1:5173/'
        Write-Host 'API documentation:     http://127.0.0.1:8000/docs'
        exit 0
    }
    Start-Sleep -Seconds 1
}

throw "The servers did not both start. See '$logDir' for details."
