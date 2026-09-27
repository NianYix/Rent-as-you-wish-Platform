# Start Cloudflare quick tunnel and write public URL into:
# - miniprogram/utils/config.js  (MODE=public, HOSTS.public)
# - backend/.env and root .env   (PUBLIC_BASE_URL)
#
# Called by scripts\start-cloudflare-tunnel.bat

$ErrorActionPreference = "Continue"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

function Find-Cloudflared {
  $cmd = Get-Command cloudflared -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $fallback = "E:\JerrySoftware\cloudflared\cloudflared.exe"
  if (Test-Path $fallback) { return $fallback }
  throw "cloudflared not found. Install it or add to PATH."
}

function Update-AppConfig([string]$PublicUrl) {
  $configPath = Join-Path $Root "miniprogram\utils\config.js"
  if (-not (Test-Path $configPath)) {
    throw "Missing $configPath"
  }

  $cfg = Get-Content $configPath -Raw -Encoding UTF8

  if ($cfg -match 'const MODE\s*=\s*"[^"]+"') {
    $cfg = [regex]::Replace($cfg, 'const MODE\s*=\s*"[^"]+"', 'const MODE = "public"')
  } else {
    throw "const MODE not found in config.js"
  }

  if ($cfg -match 'public\s*:\s*"[^"]*"') {
    $cfg = [regex]::Replace($cfg, 'public\s*:\s*"[^"]*"', "public: `"$PublicUrl`"")
  } else {
    throw "public: url not found in config.js"
  }

  $utf8NoBom = New-Object System.Text.UTF8Encoding $false
  [System.IO.File]::WriteAllText($configPath, $cfg, $utf8NoBom)
  Write-Host "[OK] Updated miniprogram/utils/config.js" -ForegroundColor Green
  Write-Host "     MODE = public"
  Write-Host "     public = $PublicUrl"
}

function Update-EnvPublicBaseUrl([string]$PublicUrl) {
  foreach ($name in @("backend\.env", ".env")) {
    $envFile = Join-Path $Root $name
    if (-not (Test-Path $envFile)) { continue }
    $text = Get-Content $envFile -Raw -Encoding UTF8
    if ($null -eq $text) { $text = "" }
    if ($text -match "(?m)^PUBLIC_BASE_URL=") {
      $text = [regex]::Replace($text, "(?m)^PUBLIC_BASE_URL=.*$", "PUBLIC_BASE_URL=$PublicUrl")
    } else {
      if ($text.Length -gt 0 -and -not $text.EndsWith("`n")) { $text += "`r`n" }
      $text += "PUBLIC_BASE_URL=$PublicUrl`r`n"
    }
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($envFile, $text, $utf8NoBom)
    Write-Host "[OK] Updated $name PUBLIC_BASE_URL" -ForegroundColor Green
  }
}

$cfPath = Find-Cloudflared
Write-Host "cloudflared: $cfPath"
Write-Host "project:     $Root"
Write-Host ""

try {
  $health = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 3
  Write-Host "Backend OK: $($health.Content)"
} catch {
  Write-Host "WARNING: backend :8000 not ready. Run start.bat first." -ForegroundColor Yellow
}

$state = [hashtable]::Synchronized(@{ Url = $null })

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $cfPath
$psi.Arguments = "tunnel --url http://127.0.0.1:8000"
$psi.RedirectStandardError = $true
$psi.RedirectStandardOutput = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true

$p = New-Object System.Diagnostics.Process
$p.StartInfo = $psi

$outputHandler = {
  if ([string]::IsNullOrEmpty($EventArgs.Data)) { return }
  $line = $EventArgs.Data
  Write-Host $line
  if ($line -match "https://[a-zA-Z0-9-]+\.trycloudflare\.com") {
    $Event.MessageData.Url = $Matches[0]
  }
}

$outEvent = Register-ObjectEvent -InputObject $p -EventName OutputDataReceived -Action $outputHandler -MessageData $state
$errEvent = Register-ObjectEvent -InputObject $p -EventName ErrorDataReceived -Action $outputHandler -MessageData $state

Write-Host "Requesting quick tunnel..."
[void]$p.Start()
$p.BeginOutputReadLine()
$p.BeginErrorReadLine()

$deadline = (Get-Date).AddMinutes(2)
while (-not $state.Url -and -not $p.HasExited -and (Get-Date) -lt $deadline) {
  Start-Sleep -Milliseconds 400
}

if (-not $state.Url) {
  Write-Host ""
  Write-Host "Failed to get trycloudflare.com URL (timeout/network)." -ForegroundColor Red
  Write-Host "See docs/cloudflare-tunnel.md for named tunnel." -ForegroundColor Yellow
  if (-not $p.HasExited) { try { $p.Kill() } catch {} }
  Unregister-Event -SourceIdentifier $outEvent.Name -ErrorAction SilentlyContinue
  Unregister-Event -SourceIdentifier $errEvent.Name -ErrorAction SilentlyContinue
  exit 1
}

$url = $state.Url.TrimEnd("/")
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Public URL: $url" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
  Update-AppConfig -PublicUrl $url
  Update-EnvPublicBaseUrl -PublicUrl $url
} catch {
  Write-Host "Failed to write config: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Next: recompile miniprogram; restart backend for PUBLIC_BASE_URL."
Write-Host "Keep this window open. Ctrl+C stops the tunnel."
Write-Host ""

try {
  while (-not $p.HasExited) { Start-Sleep -Seconds 2 }
} finally {
  Unregister-Event -SourceIdentifier $outEvent.Name -ErrorAction SilentlyContinue
  Unregister-Event -SourceIdentifier $errEvent.Name -ErrorAction SilentlyContinue
  Get-EventSubscriber | Where-Object { $_.SourceObject -eq $p } | Unregister-Event -ErrorAction SilentlyContinue
}

exit $(if ($null -ne $p.ExitCode) { $p.ExitCode } else { 0 })
