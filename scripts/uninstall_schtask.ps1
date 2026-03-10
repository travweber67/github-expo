param(
  [string]$TaskName = "GitHubExpoDaily"
)

schtasks /Query /TN $TaskName 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Task '$TaskName' not found."
  exit 0
}

schtasks /Delete /TN $TaskName /F
Write-Host "Deleted scheduled task '$TaskName'"
