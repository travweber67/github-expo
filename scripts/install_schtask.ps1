param(
  [string]$TaskName = "GitHubExpoDaily",
  [string]$RunTime = "08:00",
  [switch]$Force
)

# Use a stable, no-space path for Task Scheduler by creating a junction.
$junction = "C:\github-expo"
$target = (Resolve-Path "$PSScriptRoot\.." ).Path

if (!(Test-Path $junction)) {
  cmd.exe /c "mklink /J $junction `"$target`"" | Out-Null
}

$taskRunner = "$junction\scripts\run_daily.cmd"

# Remove existing task
schtasks /Query /TN $TaskName 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
  if ($Force) {
    $p = Start-Process schtasks.exe -ArgumentList @('/Delete','/TN',$TaskName,'/F') -NoNewWindow -Wait -PassThru
    if ($p.ExitCode -ne 0) { throw "Failed to delete existing task" }
  } else {
    Write-Host "Task '$TaskName' already exists. Re-run with -Force to replace."
    exit 0
  }
}

$args = @(
  '/Create',
  '/TN', $TaskName,
  '/SC', 'DAILY',
  '/ST', $RunTime,
  '/TR', $taskRunner,
  '/RL', 'LIMITED',
  '/RU', ('"' + $env:USERNAME + '"'),
  '/IT',
  '/F'
)

$p2 = Start-Process schtasks.exe -ArgumentList $args -NoNewWindow -Wait -PassThru
if ($p2.ExitCode -ne 0) { throw "Failed to create scheduled task" }

Write-Host "Created scheduled task '$TaskName' to run daily at $RunTime"
Write-Host "Task To Run: $taskRunner"
Write-Host "Run-as: $($env:USERNAME) (interactive only)"
