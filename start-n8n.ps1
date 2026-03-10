$ErrorActionPreference = "Stop"

# Load .env file
$envPath = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envPath)) {
    Write-Host ".env file not found!" -ForegroundColor Red
    exit 1
}

foreach ($line in Get-Content $envPath -Encoding UTF8) {
    if ($line -match '^\s*#') { continue }
    if ($line -match '^\s*$') { continue }
    $idx = $line.IndexOf('=')
    if ($idx -lt 0) { continue }
    $k = $line.Substring(0, $idx).Trim()
    $v = $line.Substring($idx + 1).Trim()
    [System.Environment]::SetEnvironmentVariable($k, $v, 'Process')
    Write-Host "  SET $k" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting n8n on http://localhost:5678" -ForegroundColor Cyan
n8n start
