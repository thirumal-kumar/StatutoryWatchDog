#!/usr/bin/env python3
import asyncio
import json
import logging
import os
import re
import sys
import requests
from pyppeteer import launch
from bs4 import BeautifulSoup

BOT_TOKEN = "8377225686:AAFMPn2JGtctZvBDJNte1LNq6zK26jRtIgA"
CHAT_ID = "324115796"
STATE_FILE = "seen.json"
MAX_MSG_LEN = 3500

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

TARGETS = {
    "UGC Notices": "https://www.ugc.gov.in/Notices",
    "UGC Incorporation": "https://www.ugc.gov.in/incorp",
    "NMC All News": "https://www.nmc.org.in/all-news/",
    "DCI India": "https://dciindia.gov.in/NewsEvents.aspx",
    "INC Nursing": "https://indiannursingcouncil.org/NewsEvents",
    "PCI Circulars": "https://pci.gov.in/news-event",
    "MCC UG Medical": "https://mcc.nic.in/ug-medical-counselling/",
    "MCC MDS": "https://mcc.nic.in/mds-counselling/",
    "MCC PG": "https://mcc.nic.in/pg-medical-counselling/",
    "NCAHP CircularOrders": "https://ncahp.abdm.gov.in/CircularOrders",
    "NCAHP WhatWeDo": "https://ncahp.abdm.gov.in/WhatWeDo",
    "DGEHS Circulars": "https://dgehs.delhi.gov.in/circulars-orders",
}

def load_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen_set):
    with open(STATE_FILE, "w") as f:
        json.dump(list(seen_set), f)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=20)
        if not resp.ok:
            logging.error(f"Telegram send failed: {resp.text}")
    except Exception as e:
        logging.error(f"Telegram send exception: {e}")

async def fetch_with_browser(url):
    browser = await launch(headless=True, args=["--no-sandbox"])
    page = await browser.newPage()
    await page.goto(url, {"waitUntil": "networkidle2", "timeout": 60000})
    html = await page.content()
    await browser.close()
    return html

def extract_links(html, label):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        title = re.sub(r"\s+", " ", a.get_text(strip=True))
        href = a["href"]
        if not href.lower().startswith("http"):
            continue
        if not title:
            continue
        out.append((title, href))
    return out

async def main():
    seen = load_seen()
    digest_parts = []

    for label, url in TARGETS.items():
        logging.info(f"🔎 Checking: {label}")
        try:
            html = await fetch_with_browser(url)
            items = extract_links(html, label)

            new_items = []
            for title, link in items:
                if link not in seen:
                    new_items.append((title, link))
                    seen.add(link)

            if new_items:
                section_text = f"<b>{label}</b>\n"
                for title, link in new_items:
                    section_text += f"• {title}\n🔗 {link}\n"
            else:
                section_text = f"<b>{label}</b>\nNo new updates today. ✅\n"

            digest_parts.append(section_text)

        except Exception as e:
            digest_parts.append(f"<b>{label}</b>\n⚠️ Error fetching data: {e}\n")

    save_seen(seen)

    # send section-wise digest
    for section in digest_parts:
        while section:
            chunk = section[:MAX_MSG_LEN]
            send_telegram_message(chunk)
            section = section[MAX_MSG_LEN:]

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit(0)

