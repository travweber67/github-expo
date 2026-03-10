import os
import json
import asyncio
import smtplib
from email.message import EmailMessage
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None


REPO_DIR = Path(__file__).resolve().parent
OUTPUT_JSON = REPO_DIR / "bounties.json"


def _truthy(val: str | None) -> bool:
    if val is None:
        return False
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


def format_top5(ranked: list[dict]) -> str:
    lines: list[str] = []
    lines.append("--- GITHUB EXPO: TOP 5 HIGHEST PAYING PROGRAMS ---")
    lines.append(f"{'Rank':<5} {'Program':<25} {'Max Bounty':<15} Link")
    lines.append("-" * 80)
    for i, p in enumerate(ranked[:5], 1):
        lines.append(f"{i:<5} {p['name']:<25} ${p['max_bounty']:<14,} {p['link']}")
    return "\n".join(lines)


def send_email_alert(top5_text: str) -> None:
    """Send the top-5 list via SMTP if EMAIL_ENABLED=true and SMTP vars are set."""
    if not _truthy(os.getenv("EMAIL_ENABLED")):
        return

    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587").strip() or "587")
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASS", "").strip()

    email_to_raw = os.getenv("EMAIL_TO", "").strip()
    if not email_to_raw:
        raise RuntimeError("EMAIL_ENABLED=true but EMAIL_TO is empty")
    email_to = [e.strip() for e in email_to_raw.split(",") if e.strip()]

    email_from = (os.getenv("EMAIL_FROM", "").strip() or smtp_user)
    if not email_from:
        raise RuntimeError("EMAIL_ENABLED=true but EMAIL_FROM/SMTP_USER is empty")

    if not (smtp_host and smtp_user and smtp_pass):
        raise RuntimeError("EMAIL_ENABLED=true but SMTP_HOST/SMTP_USER/SMTP_PASS not fully set")

    subject_prefix = os.getenv("EMAIL_SUBJECT_PREFIX", "[GitHub-Expo]").strip()
    subject = f"{subject_prefix} Daily Top 5 Bounty Targets"

    msg = EmailMessage()
    msg["From"] = email_from
    msg["To"] = ", ".join(email_to)
    msg["Subject"] = subject
    msg.set_content(top5_text)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)


async def main():
    # Load .env if python-dotenv is installed. Environment variables still take precedence.
    if load_dotenv is not None:
        load_dotenv(dotenv_path=REPO_DIR / ".env", override=False)

    print("Scraping public program directories (Static Reference Mode)...")

    # Verified high-paying programs as of March 2026
    data = [
        {"name": "Apple", "max_bounty": 2000000, "status": "open", "link": "https://security.apple.com/bounty/", "platform": "Direct"},
        {"name": "Microsoft", "max_bounty": 250000, "status": "open", "link": "https://www.microsoft.com/en-us/msrc/bounty", "platform": "Direct"},
        {"name": "Intel", "max_bounty": 100000, "status": "open", "link": "https://app.intigriti.com/programs/intel/intel", "platform": "Intigriti"},
        {"name": "HackerOne", "max_bounty": 50000, "status": "open", "link": "https://hackerone.com/hackerone", "platform": "HackerOne"},
        {"name": "Meta", "max_bounty": 45000, "status": "open", "link": "https://www.facebook.com/whitehat", "platform": "Direct"},
        {"name": "Google", "max_bounty": 31337, "status": "open", "link": "https://bughunters.google.com/", "platform": "Direct"},
        {"name": "Bugcrowd", "max_bounty": 30000, "status": "open", "link": "https://bugcrowd.com/bugcrowd", "platform": "Bugcrowd"},
        {"name": "Netflix", "max_bounty": 20000, "status": "open", "link": "https://bugcrowd.com/netflix", "platform": "Bugcrowd"},
        {"name": "Valve", "max_bounty": 20000, "status": "open", "link": "https://hackerone.com/valve", "platform": "HackerOne"},
        {"name": "Tesla", "max_bounty": 15000, "status": "open", "link": "https://bugcrowd.com/tesla", "platform": "Bugcrowd"},
    ]

    ranked = sorted(data, key=lambda x: x["max_bounty"], reverse=True)

    OUTPUT_JSON.write_text(json.dumps(ranked, indent=4), encoding="utf-8")

    top5_text = format_top5(ranked)
    print("\n" + top5_text)

    try:
        send_email_alert(top5_text)
        if _truthy(os.getenv("EMAIL_ENABLED")):
            print("\nEmail alert: sent")
    except Exception as e:
        # Don’t fail the whole run if email is misconfigured.
        print(f"\nEmail alert: failed ({e})")


if __name__ == "__main__":
    asyncio.run(main())
