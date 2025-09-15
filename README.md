# 📢 Statutory WatchDog Bot

A Telegram bot that automatically checks key statutory/regulatory portals (UGC, NMC, PCI, INC, DCI, MCC, NCAHP, DGEHS, etc.) and sends daily updates at **9:00 AM IST**.  
It is designed to run **serverless on GitHub Actions**, so it works even if your local workstation is off.

---

## 🚀 Features
- Monitors multiple portals:
  - UGC Notices, UGC Incorporation
  - NMC All News
  - DCI India
  - INC Nursing
  - PCI Circulars
  - MCC UG / MDS / PG
  - NCAHP Circulars & WhatWeDo
  - DGEHS Circulars
- Fetches **new updates only** (not the entire history).
- Posts updates to a configured **Telegram bot chat**.
- Sends daily consolidated digest (with clear portal-wise separation).
- Automatic scheduling via **GitHub Actions**.

---

## ⚙️ Setup

### 1. Create a Telegram Bot
1. Open Telegram and search for **@BotFather**.
2. Run `/newbot` → give a name and username.
3. Copy the **bot token** you receive (format: `123456:ABC-DEF1234ghIkl...`).

### 2. Get Your Chat ID
1. Start your bot with `/start`.
2. Visit:  
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for `"chat":{"id":...}` → that’s your chat ID.

---

## 🔐 GitHub Secrets
Go to your repo → **Settings** → **Secrets and variables** → **Actions**.

Add two repository secrets:
- `BOT_TOKEN` → your Telegram bot token  
- `CHAT_ID` → your Telegram chat ID  

---

## 🕒 Scheduling
This project runs automatically at **9:00 AM IST** every day.

GitHub Actions cron is set to:  
```yaml
schedule:
  - cron: '30 3 * * *'   # 03:30 UTC = 09:00 IST


📂 Repository Structure
.github/workflows/daily.yml   # GitHub Actions workflow file
watchdog_full_digest_split.py # Main scraper + Telegram sender
README.md                     # Documentation (this file)


📬 Output Example

Each day, the bot posts a digest like this:

📢 Daily Update Report

UGC Notices
• Title of latest notice
🔗 https://www.ugc.gov.in/...

NMC All News
✅ No new updates today. Will check again tomorrow.

PCI Circulars
• Circular title
🔗 https://pci.gov.in/en/blog/...

🛠️ Tech Stack

Python 3.11

requests, beautifulsoup4, pyppeteer

GitHub Actions for automation

Telegram Bot API

📜 License

MIT License – feel free to use and adapt with credit.
