<#
.SYNOPSIS
    Smart Farming All-in-One Service Launcher
    Starts Backend API (8000), Model Inference Server (8001), Frontend UI (5173), and ARQ Redis Worker.

.PARAMETER SeparateWindows
    Launch each service in a separate Command Prompt window instead of unified live streaming.
#>

param(
    [Alias("s", "windowed", "windows")]
    [switch]$SeparateWindows,

    [Alias("m", "mobile")]
    [switch]$IncludeMobile
)

$root = (Resolve-Path "$PSScriptRoot\..").Path
$backend = Join-Path $root 'backend'
$frontend = Join-Path $root 'frontend'
$model = Join-Path $root 'model_service'
$mobile = Join-Path $root 'mobile'
$uvicorn = Join-Path $backend '.venv\Scripts\uvicorn.exe'
$arq = Join-Path $backend '.venv\Scripts\arq.exe'

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "              SMART FARMING - STARTING" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[SYSTEM] Project Root: " -ForegroundColor DarkGray -NoNewline
Write-Host $root -ForegroundColor White
if ($IncludeMobile) {
    Write-Host "[SYSTEM] Mobile Mode:  " -ForegroundColor DarkGray -NoNewline
    Write-Host "Enabled (Chrome device target)" -ForegroundColor Cyan
}
Write-Host ""

if ($SeparateWindows) {
    Write-Host "[MODE] Launching services in separate windows..." -ForegroundColor Yellow
    Write-Host ""

    Write-Host "[1/4] Starting Server 1: Backend API (Port 8000)..." -ForegroundColor Green
    Start-Process cmd.exe -ArgumentList "/k", "cd /d `"$backend`" && `"$uvicorn`" src.app.main:app --host 127.0.0.1 --port 8000 --reload"

    Write-Host "[2/4] Starting Server 2: Model Inference Server (Port 8001)..." -ForegroundColor Blue
    Start-Process cmd.exe -ArgumentList "/k", "cd /d `"$model`" && `"$uvicorn`" main:app --host 127.0.0.1 --port 8001 --reload"

    Write-Host "[3/4] Starting Server 3: Frontend (Port 5173)..." -ForegroundColor Magenta
    Start-Process cmd.exe -ArgumentList "/k", "cd /d `"$frontend`" && npm run dev"

    Write-Host "[4/4] Starting Server 4: ARQ Worker (Redis Queue)..." -ForegroundColor Yellow
    Start-Process cmd.exe -ArgumentList "/k", "cd /d `"$backend`" && set PYTHONIOENCODING=utf-8 && `"$arq`" src.app.worker.WorkerSettings"

    if ($IncludeMobile) {
        Write-Host "[5/5] Starting Server 5: Mobile App (Flutter in Chrome)..." -ForegroundColor Cyan
        Start-Process cmd.exe -ArgumentList "/k", "cd /d `"$mobile`" && flutter run -d chrome"
    }

    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "              ALL SERVICES LAUNCHED" -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  BACKEND   -> http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "  MODEL     -> http://127.0.0.1:8001" -ForegroundColor Blue
    Write-Host "  FRONTEND  -> http://localhost:5173" -ForegroundColor Magenta
    Write-Host "  ARQ       -> Redis background worker" -ForegroundColor Yellow
    if ($IncludeMobile) {
        Write-Host "  MOBILE    -> Flutter Web (Chrome)" -ForegroundColor Cyan
    }
    Write-Host ""
    Write-Host "Each service is running in its own titled window." -ForegroundColor DarkGray
    return
}

# --- Unified Streaming Mode (Non-blocking event-driven) ---
$services = @()

function Start-ServiceProcess($name, $workingDir, $exePath, $argsString, $color) {
    Write-Host "[$name] Starting..." -ForegroundColor $color

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $exePath
    $psi.Arguments = $argsString
    $psi.WorkingDirectory = $workingDir
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true

    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    $p.EnableRaisingEvents = $true

    # Register non-blocking event handlers for stdout and stderr
    Register-ObjectEvent -InputObject $p -EventName "OutputDataReceived" -MessageData @{ Name=$name; Color=$color } -Action {
        if ($EventArgs.Data) {
            Write-Host ("[" + $Event.MessageData.Name.PadRight(8) + "] ") -ForegroundColor $Event.MessageData.Color -NoNewline
            Write-Host $EventArgs.Data
        }
    } | Out-Null

    Register-ObjectEvent -InputObject $p -EventName "ErrorDataReceived" -MessageData @{ Name=$name; Color=$color } -Action {
        if ($EventArgs.Data) {
            Write-Host ("[" + $Event.MessageData.Name.PadRight(8) + "] ") -ForegroundColor $Event.MessageData.Color -NoNewline
            Write-Host $EventArgs.Data
        }
    } | Out-Null

    $p.Start() | Out-Null
    $p.BeginOutputReadLine()
    $p.BeginErrorReadLine()

    return @{ Name=$name; Process=$p; Color=$color; ReportedExit=$false }
}

$services += Start-ServiceProcess 'BACKEND' $backend $uvicorn 'src.app.main:app --host 127.0.0.1 --port 8000 --reload' 'Green'
$services += Start-ServiceProcess 'MODEL' $model $uvicorn 'main:app --host 127.0.0.1 --port 8001 --reload' 'Blue'
$services += Start-ServiceProcess 'FRONTEND' $frontend 'cmd.exe' '/c npm run dev' 'Magenta'

# Set environment variable for ARQ Indic encoding
$env:PYTHONIOENCODING = "utf-8"
$services += Start-ServiceProcess 'ARQ' $backend $arq 'src.app.worker.WorkerSettings' 'Yellow'

if ($IncludeMobile) {
    $services += Start-ServiceProcess 'MOBILE' $mobile 'cmd.exe' '/c flutter run -d chrome' 'Cyan'
}

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "              ALL SERVICES RUNNING" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  BACKEND   -> http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  MODEL     -> http://127.0.0.1:8001" -ForegroundColor Blue
Write-Host "  FRONTEND  -> http://localhost:5173" -ForegroundColor Magenta
Write-Host "  ARQ       -> Redis background worker" -ForegroundColor Yellow
if ($IncludeMobile) {
    Write-Host "  MOBILE    -> Flutter Web (Chrome)" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "Press Ctrl+C to stop all services cleanly." -ForegroundColor DarkGray
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "                 LIVE LOGS" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

function Stop-AllServices {
    Write-Host ""
    Write-Host "Stopping all services..." -ForegroundColor Yellow
    foreach ($svc in $services) {
        $p = $svc.Process
        if ($p -and -not $p.HasExited) {
            Write-Host "Killing $($svc.Name) (PID $($p.Id))..." -ForegroundColor DarkGray
            try {
                cmd.exe /c "taskkill /pid $($p.Id) /t /f >nul 2>&1"
            } catch {}
        }
    }
    Get-EventSubscriber | Unregister-Event -ErrorAction SilentlyContinue
    Write-Host "All services stopped." -ForegroundColor Green
}

try {
    while ($true) {
        foreach ($svc in $services) {
            $p = $svc.Process
            if ($p.HasExited -and -not $svc.ReportedExit) {
                Write-Host ("[" + $svc.Name.PadRight(8) + "] PROCESS EXITED - Code: " + $p.ExitCode) -ForegroundColor Red
                $svc.ReportedExit = $true
            }
        }
        Start-Sleep -Milliseconds 250
    }
}
finally {
    Stop-AllServices
}
