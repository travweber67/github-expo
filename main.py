import asyncio
import json
import os
from playwright.async_api import async_playwright
from tabulate import tabulate

async def scrape_hackerone(page):
    print("Scraping HackerOne...")
    await page.goto("https://hackerone.com/directory/programs?order_direction=desc&order_field=started_at", wait_until="networkidle")
    # This page is dynamic. Let's wait for elements.
    await page.wait_for_selector(".table-container")
    
    programs = []
    # HackerOne directory usually shows a list of programs.
    # Note: Precise selectors might change, but this is a robust attempt.
    rows = await page.query_selector_all("tr.da-table-row")
    for row in rows[:20]: # Top 20 for brevity
        name_el = await row.query_selector(".da-table-cell--name")
        bounty_el = await row.query_selector(".da-table-cell--bounty") # This might be different now
        link_el = await name_el.query_selector("a") if name_el else None
        
        if name_el and link_el:
            name = await name_el.inner_text()
            link = "https://hackerone.com" + await link_el.get_attribute("href")
            # Max bounty is often hidden or requires hovering.
            # For the expo, we'll try to find any bounty mention.
            bounty_text = await bounty_el.inner_text() if bounty_el else "N/A"
            programs.append({
                "name": name.strip(),
                "max_bounty": bounty_text.strip(),
                "status": "open",
                "link": link,
                "platform": "HackerOne"
            })
    return programs

async def scrape_bugcrowd(page):
    print("Scraping Bugcrowd...")
    await page.goto("https://bugcrowd.com/programs", wait_until="networkidle")
    await page.wait_for_selector(".bc-panel")
    
    programs = []
    cards = await page.query_selector_all(".bc-panel")
    for card in cards[:20]:
        name_el = await card.query_selector("h4")
        bounty_el = await card.query_selector(".bc-stats__item--bounty .bc-stats__value")
        link_el = await card.query_selector("a.bc-panel__link")
        
        if name_el and link_el:
            name = await name_el.inner_text()
            link = "https://bugcrowd.com" + await link_el.get_attribute("href")
            bounty = await bounty_el.inner_text() if bounty_el else "N/A"
            programs.append({
                "name": name.strip(),
                "max_bounty": bounty.strip(),
                "status": "open",
                "link": link,
                "platform": "Bugcrowd"
            })
    return programs

async def scrape_intigriti(page):
    print("Scraping Intigriti...")
    await page.goto("https://app.intigriti.com/programs", wait_until="networkidle")
    # Intigriti uses a grid/list.
    await page.wait_for_selector(".program-card")
    
    programs = []
    cards = await page.query_selector_all(".program-card")
    for card in cards[:20]:
        name_el = await card.query_selector(".program-name")
        bounty_el = await card.query_selector(".bounty-range")
        link_el = await card.query_selector("a")
        
        if name_el and link_el:
            name = await name_el.inner_text()
            link = "https://app.intigriti.com" + await link_el.get_attribute("href")
            bounty = await bounty_el.inner_text() if bounty_el else "N/A"
            programs.append({
                "name": name.strip(),
                "max_bounty": bounty.strip(),
                "status": "open",
                "link": link,
                "platform": "Intigriti"
            })
    return programs

def clean_bounty(bounty_str):
    if not bounty_str or bounty_str == "N/A":
        return 0
    # Extract digits. e.g., "$10,000" -> 10000
    cleaned = "".join(c for c in bounty_str if c.isdigit())
    return int(cleaned) if cleaned else 0

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        page = await context.new_page()
        
        all_programs = []
        
        try:
            h1 = await scrape_hackerone(page)
            all_programs.extend(h1)
        except Exception as e:
            print(f"Error scraping HackerOne: {e}")
            
        try:
            bc = await scrape_bugcrowd(page)
            all_programs.extend(bc)
        except Exception as e:
            print(f"Error scraping Bugcrowd: {e}")
            
        try:
            inti = await scrape_intigriti(page)
            all_programs.extend(inti)
        except Exception as e:
            print(f"Error scraping Intigriti: {e}")
            
        # Rank by bounty
        all_programs.sort(key=lambda x: clean_bounty(x["max_bounty"]), reverse=True)
        
        # Save to file
        with open("bounties.json", "w") as f:
            json.dump(all_programs, f, indent=4)
        
        # Print table
        table_data = [[p["name"], p["max_bounty"], p["platform"], p["link"]] for p in all_programs[:20]]
        print("\n=== TOP BOUNTY PROGRAMS ===")
        print(tabulate(table_data, headers=["Program", "Max Bounty", "Platform", "Link"]))
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
