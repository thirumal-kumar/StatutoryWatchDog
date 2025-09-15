import asyncio
import logging
import requests
from pyppeteer import launch

# --- CONFIG ---
TELEGRAM_BOT_TOKEN = "8377225686:AAFMPn2JGtctZvBDJNte1LNq6zK26jRtIgA"
TELEGRAM_CHAT_ID = "324115796"

sections = {
    "UGC Notices": "https://www.ugc.gov.in/",
    "UGC Incorporation": "https://www.ugc.gov.in/page/miscellaneous.aspx",
    "NMC All News": "https://www.nmc.org.in/",
    "DCI India": "https://dciindia.gov.in/",
    "INC Nursing": "https://www.indiannursingcouncil.org/",
    "PCI Circulars": "https://pci.nic.in/",
    "MCC UG Medical": "https://mcc.nic.in/ug-medical-counselling/",
    "MCC MDS": "https://mcc.nic.in/mds-counselling/",
    "MCC PG": "https://mcc.nic.in/pg-medical-counselling/",
    "NCAHP CircularOrders": "https://ncahp.abdm.gov.in/CircularOrders",
    "NCAHP WhatWeDo": "https://ncahp.abdm.gov.in/WhatWeDo",
    "DGEHS Circulars": "https://dgehs.delhi.gov.in/"
}

# --- LOGGING ---
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")

# --- HELPERS ---
async def fetch_links(url):
    """Scrape links using headless Chromium."""
    browser = await launch(headless=True, args=["--no-sandbox"])
    page = await browser.newPage()
    try:
        await page.goto(url, timeout=60000)
        anchors = await page.querySelectorAllEval("a", "(els => els.map(a => [a.innerText.trim(), a.href]))")
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        anchors = []
    await browser.close()
    return anchors

def clean_mcc_links(links):
    """Filter MCC links: remove junk, keep only valid PDFs/notices."""
    results = []
    for text, href in links:
        if not href:
            continue
        skip_patterns = ["sitemap", "archive", "contact", "about", "facebook",
                         "twitter", "linkedin", "gov.in", "mohfw"]
        if any(p in href.lower() for p in skip_patterns):
            continue
        if text.lower() in ["home", "mcc", "ug medical", "pg medical", "super speciality", "mds"]:
            continue
        if href.endswith(".pdf") or "mcc.nic.in" in href:
            results.append((text if text else "Notice", href))
    return results[:5]  # limit to latest 5

def format_digest(updates):
    """Format updates as single digest message."""
    digest = "📰 *Daily Update Report*\n\n"
    for section, links in updates.items():
        digest += f"*{section}*\n"
        if not links:
            digest += "✅ No new updates today. Will check again tomorrow.\n\n"
        else:
            for text, href in links:
                digest += f"• {text}\n🔗 {href}\n"
            digest += "\n"
    return digest

def send_telegram_message(message):
    """Send message to Telegram with Markdown formatting."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code != 200:
            logging.error(f"Telegram send failed: {resp.text}")
        else:
            logging.info("✅ Sent digest to Telegram")
    except Exception as e:
        logging.error(f"Telegram error: {e}")

# --- MAIN ---
async def main():
    updates = {}
    for name, url in sections.items():
        logging.info(f"🔎 Checking: {name}")
        links = await fetch_links(url)

        if "MCC" in name:  # special filter for MCC sites
            links = clean_mcc_links(links)

        updates[name] = links
    digest = format_digest(updates)
    send_telegram_message(digest)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
