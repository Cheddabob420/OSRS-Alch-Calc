#!/home/pi/.venv/bin/python3
from datetime import datetime
import json
import requests
import alch_engine  # Assumes your main engine file is named alch_engine.py

# Configuration
OUTPUT_JSON_FILE = "/home/dietpi/osrs/live_alchs.json"

def fetch_raw_api_prices():
    """Helper to fetch raw prices block so both functions can use it."""
    url = "https://prices.runescape.wiki/api/v1/osrs/latest"
    headers = {'User-Agent': 'Learning-OSRS-API/1.0 (Email: cogygibson420@gmail.com)'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("data", {})
    except Exception as e:
        print(f"Error downloading live price block: {e}")
        return {}

def run_dashboard_pipeline():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Executing data refresh...")
    
    # 1. Fetch raw prices block directly from the Wiki API
    live_prices_block = fetch_raw_api_prices()
    
    # 2. Fetch your static item mappings database
    base_items = alch_engine.get_item_data()
    
    if not live_prices_block or not base_items:
        print("❌ Pipeline failed: Essential API data was unreachable.")
        return

    # 3. Calculate High Alchs (Passing your base items)
    # Note: Make sure your find_alch_opportunities uses the live data internally
    profitable_alchs, nature_rune_cost = alch_engine.find_alch_opportunities(base_items)
    
    # 4. Calculate Skilling Margins (Passing the raw live prices block)
    processing_deals = alch_engine.calculate_processing_profits(live_prices_block)
    
    # 5. Pack everything into the exact structure the HTML page expects
    dashboard_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nature_rune_cost": nature_rune_cost,
        "alch_items": profitable_alchs,
        "processing_items": processing_deals
    }
    
    # 6. Overwrite the file
    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=4, ensure_ascii=False)
        
    print(f"🎉 Success! Found {len(profitable_alchs)} alchs and {len(processing_deals)} skilling methods.")

if __name__ == "__main__":
    run_dashboard_pipeline()
