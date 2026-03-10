# GitHub Expo

A small “daily money-maker” helper: ranks high-paying public bug bounty programs, saves results to `bounties.json`, prints a clean Top-5, and (optionally) emails the Top-5 each run.

## What it does
- Writes ranked results to `bounties.json`
- Prints a clean Top-5 table to stdout
- Optional email alert with the same Top-5 text (SMTP)
- Optional Windows Task Scheduler job to run daily at 8:00 AM

## Setup

### 1) Install dependencies
```bash
pip install -r requirements.txt
```

### 2) (Optional) Enable email alerts
This project does **not** hardcode credentials.

1. Copy the template:
   ```bash
   copy .env.example .env
   ```
2. Edit `.env` and set:
   - `EMAIL_ENABLED=true`
   - `EMAIL_TO=travweber67@gmail.com`
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`

Notes:
- For Gmail, use an **App Password** (recommended) instead of your normal password.
- `.env` is ignored by git.

### 3) Run it
```bash
python main.py
```

## Daily automation (Windows Task Scheduler)
Creates a per-user scheduled task named `GitHubExpoDaily` that runs every day at **8:00 AM**.

From PowerShell:
```powershell
cd $HOME\github-expo
powershell -ExecutionPolicy Bypass -File .\scripts\install_schtask.ps1

# Verify
schtasks /Query /TN GitHubExpoDaily
```

To remove:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_schtask.ps1
```

Logs (when scheduled):
- `logs\run.log`
- `logs\error.log`
