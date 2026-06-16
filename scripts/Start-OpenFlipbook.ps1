$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RepoRoot "apps\modal-backend"
$WebDir = Join-Path $RepoRoot "apps\web"
$WorkDir = Join-Path $RepoRoot "work"
$ImageDir = Join-Path ([Environment]::GetFolderPath("Desktop")) "flipbook_images"
$BackendLog = Join-Path $WorkDir "desktop-backend.log"
$WebLog = Join-Path $WorkDir "desktop-web.log"
$Url = "http://localhost:3000"

New-Item -ItemType Directory -Force -Path $WorkDir, $ImageDir | Out-Null

function Import-EnvFile {
  param([string]$Path)
  if (!(Test-Path $Path)) { return }
  Get-Content $Path | ForEach-Object {
    $line = $_.Trim()
    if (!$line -or $line.StartsWith("#") -or !$line.Contains("=")) { return }
    $parts = $line.Split("=", 2)
    $name = $parts[0].Trim()
    $value = $parts[1].Trim().Trim('"').Trim("'")
    if ($name) {
      [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
  }
}

function Stop-ProjectProcessOnPort {
  param([int]$Port)
  $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
  foreach ($connection in $connections) {
    $processId = $connection.OwningProcess
    if (!$processId) { continue }
    $proc = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
    if ($proc -and $proc.CommandLine -like "*openflipbook*") {
      Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
  }
}

function Wait-ForHttp {
  param([string]$TargetUrl, [int]$Seconds = 45)
  $deadline = (Get-Date).AddSeconds($Seconds)
  while ((Get-Date) -lt $deadline) {
    try {
      $response = Invoke-WebRequest -UseBasicParsing -Uri $TargetUrl -TimeoutSec 3
      if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) { return $true }
    } catch {
      Start-Sleep -Seconds 1
    }
  }
  return $false
}

Import-EnvFile (Join-Path $WebDir ".env.local")
Import-EnvFile (Join-Path $BackendDir "env.local")
Import-EnvFile (Join-Path $BackendDir ".env")

$env:MODAL_API_URL = "http://127.0.0.1:8000"
$env:PORT = "8000"
$env:NEXT_PUBLIC_LOCAL_STORAGE_ENABLED = "true"
$env:NEXT_PUBLIC_LOCAL_IMAGES_BASE_URL = "/local_images"
$env:LOCAL_STORAGE_PATH = $ImageDir
$env:USE_LOCAL_STORAGE = "true"

Stop-ProjectProcessOnPort 3000
Stop-ProjectProcessOnPort 8000

$uv = "D:\python\python\Scripts\uv.exe"
if (!(Test-Path $uv)) { $uv = "uv" }

Start-Process `
  -FilePath $uv `
  -ArgumentList "run --with-requirements requirements.txt python local_server.py" `
  -WorkingDirectory $BackendDir `
  -RedirectStandardOutput $BackendLog `
  -RedirectStandardError $BackendLog.Replace(".log", ".err.log") `
  -WindowStyle Hidden

Start-Sleep -Seconds 2

Start-Process `
  -FilePath "pnpm.cmd" `
  -ArgumentList "--filter @openflipbook/web dev" `
  -WorkingDirectory $RepoRoot `
  -RedirectStandardOutput $WebLog `
  -RedirectStandardError $WebLog.Replace(".log", ".err.log") `
  -WindowStyle Hidden

if (Wait-ForHttp $Url 60) {
  Start-Process $Url
  Write-Host "OpenFlipbook is running at $Url"
  Write-Host "Images folder: $ImageDir"
} else {
  Write-Host "OpenFlipbook did not become ready in time."
  Write-Host "Backend log: $BackendLog"
  Write-Host "Web log: $WebLog"
}
