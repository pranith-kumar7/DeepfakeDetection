$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $projectRoot "backend"
$frontendPath = Join-Path $projectRoot "frontend"
$pythonPath = Join-Path $projectRoot "tf_env\Scripts\python.exe"

if (-not (Test-Path $pythonPath)) {
    Write-Host "Python environment not found at $pythonPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Write-Host "Installing frontend dependencies..."
    Push-Location $frontendPath
    npm install
    Pop-Location
}

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$backendPath'; &'$pythonPath' app.py"
)

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$frontendPath'; npm start"
)

Write-Host "Backend starting at http://localhost:5000" -ForegroundColor Green
Write-Host "Frontend starting at http://localhost:3000" -ForegroundColor Green
