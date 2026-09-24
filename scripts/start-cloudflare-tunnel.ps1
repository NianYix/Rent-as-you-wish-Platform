# 启动 Cloudflare 临时隧道，自动写回小程序与后端公网地址
# 用法: powershell -ExecutionPolicy Bypass -File scripts\start-cloudflare-tunnel.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $Root) { $Root = (Get-Location).Path }

$cf = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cf) {
  $fallback = "E:\JerrySoftware\cloudflared\cloudflared.exe"
  if (Test-Path $fallback) { $cfPath = $fallback } else { throw "cloudflared not found" }
} else {
  $cfPath = $cf.Source
}

try {
  $health = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 3
  Write-Host "Backend OK:" $health.Content
} catch {
  Write-Host "WARNING: backend 8000 not reachable. Start start.bat first." -ForegroundColor Yellow
}

Write-Host "Starting Cloudflare quick tunnel..."
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $cfPath
$psi.Arguments = "tunnel --url http://127.0.0.1:8000"
$psi.RedirectStandardError = $true
$psi.RedirectStandardOutput = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$p = New-Object System.Diagnostics.Process
$p.StartInfo = $psi

$url = $null
$handler = {
  param($sender, $e)
  if (-not $e.Data) { return }
  Write-Host $e.Data
  if ($e.Data -match "https://[a-zA-Z0-9-]+\.trycloudflare\.com") {
    $script:url = $Matches[0]
  }
}
$p.add_OutputDataReceived($handler)
$p.add_ErrorDataReceived($handler)
[void]$p.Start()
$p.BeginOutputReadLine()
$p.BeginErrorReadLine()

$deadline = (Get-Date).AddMinutes(2)
while (-not $url -and -not $p.HasExited -and (Get-Date) -lt $deadline) {
  Start-Sleep -Milliseconds 500
}

if (-not $url) {
  Write-Host "Failed to get trycloudflare URL (network timeout?). Try named tunnel instead." -ForegroundColor Red
  Write-Host "See docs/cloudflare-tunnel.md"
  if (-not $p.HasExited) { $p.Kill() }
  exit 1
}

Write-Host ""
Write-Host "Public URL: $url" -ForegroundColor Green

# update config.js
$configPath = Join-Path $Root "miniprogram\utils\config.js"
$cfg = Get-Content $configPath -Raw -Encoding UTF8
$cfg = $cfg -replace 'const MODE = "[^"]+"', 'const MODE = "public"'
$cfg = $cfg -replace 'public:\s*"[^"]*"', ("public: `"$url`"")
Set-Content -Path $configPath -Value $cfg -Encoding UTF8
Write-Host "Updated miniprogram/utils/config.js -> MODE=public"

# update backend .env PUBLIC_BASE_URL
foreach ($envFile in @((Join-Path $Root "backend\.env"), (Join-Path $Root ".env"))) {
  if (Test-Path $envFile) {
    $envText = Get-Content $envFile -Raw -Encoding UTF8
    if ($envText -match "PUBLIC_BASE_URL=") {
      $envText = $envText -replace "PUBLIC_BASE_URL=.*", "PUBLIC_BASE_URL=$url"
    } else {
      $envText = $envText.TrimEnd() + "`r`nPUBLIC_BASE_URL=$url`r`n"
    }
    Set-Content -Path $envFile -Value $envText -Encoding UTF8
    Write-Host "Updated $envFile PUBLIC_BASE_URL"
  }
}

Write-Host ""
Write-Host "Next: recompile miniprogram, preview on phone (4G OK)."
Write-Host "Keep this window open. Ctrl+C stops tunnel."
Write-Host ""

# keep process attached
while (-not $p.HasExited) { Start-Sleep -Seconds 2 }
exit $p.ExitCode
