param(
  [string]$RepoDir = (Resolve-Path "$PSScriptRoot\..")
)

$repo = (Resolve-Path $RepoDir).Path
Set-Location $repo

$logs = Join-Path $repo "logs"
if (!(Test-Path $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }

$runLog = Join-Path $logs "run.log"
$errLog = Join-Path $logs "error.log"

try {
  & py -3 .\main.py 1>> $runLog 2>> $errLog
} catch {
  $_ | Out-String | Add-Content -Path $errLog
  exit 1
}
