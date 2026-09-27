# Write %USERPROFILE%\.cloudflared\config.yml for rent-api -> api.kinih.xyz

$ErrorActionPreference = "Stop"
$dir = Join-Path $env:USERPROFILE ".cloudflared"
if (-not (Test-Path $dir)) {
  throw "Missing $dir . Run: cloudflared tunnel login"
}

$cred = Get-ChildItem $dir -Filter "*.json" |
  Where-Object { $_.Name -ne "cert.pem" -and $_.Name -match "^[0-9a-fA-F-]{36}\.json$" } |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if (-not $cred) {
  # also accept any uuid-named json
  $cred = Get-ChildItem $dir -Filter "*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
}
if (-not $cred) {
  throw "No tunnel credentials JSON found. Run: cloudflared tunnel create rent-api"
}

$tunnelId = [System.IO.Path]::GetFileNameWithoutExtension($cred.Name)
$credPath = $cred.FullName -replace "\\", "/"

# Prefer listing tunnel to get id by name
$cf = Get-Command cloudflared -ErrorAction SilentlyContinue
$cfPath = if ($cf) { $cf.Source } else { "E:\JerrySoftware\cloudflared\cloudflared.exe" }
try {
  $list = & $cfPath tunnel list 2>&1 | Out-String
  if ($list -match "rent-api\s+([0-9a-fA-F-]{36})") {
    $tunnelId = $Matches[1]
    $credPath = (Join-Path $dir "$tunnelId.json") -replace "\\", "/"
  }
} catch {}

$configPath = Join-Path $dir "config.yml"
$yml = @"
tunnel: $tunnelId
credentials-file: $credPath

ingress:
  - hostname: api.kinih.xyz
    service: http://127.0.0.1:8000
  - service: http_status:404
"@

$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($configPath, $yml, $utf8NoBom)
Write-Host "[OK] Wrote $configPath"
Write-Host $yml
