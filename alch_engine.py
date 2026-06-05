import json
import requests

HEADERS = {
    'User-Agent': 'Learning-OSRS-API/1.0 (Email: cogygibson420@gmail.com)'
}
PRICES_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
MAPPING_URL = 'https://prices.runescape.wiki/api/v1/osrs/mapping'
NATURE_RUNE_ID = "561"


def get_item_data():
    print("Connecting to the OSRS Wiki Prices API for mappings...")
    try:
        response = requests.get(MAPPING_URL, headers=HEADERS)
        response.raise_for_status()
        raw_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching item mappings: {e}")
        return []

    cleaned_items = []
    for item in raw_data:
        extracted_info = {
            "id": item.get("id"),
            "name": item.get("name"),
            "high_alch_price": item.get("highalch", 0),
            "buy_limit": item.get("limit", 0)
        }
        cleaned_items.append(extracted_info)
    print(f"🎉 Success! Pulled {len(cleaned_items)} items")
    return cleaned_items


def find_alch_opportunities(alch_prices):
    if not alch_prices:
        return [], 124

    print("Fetching live Grand Exchange margins...")
    try:
        response = requests.get(PRICES_URL, headers=HEADERS)
        response.raise_for_status()
        live_prices = response.json().get("data", {})
    except requests.exceptions.RequestException as e:
        print(f"Error fetching live prices from API: {e}")
        return [], 124

    nat_rune_data = live_prices.get(NATURE_RUNE_ID, {})
    nat_rune_cost = nat_rune_data.get("high", 124)

    profitable_items = []
    for item_info in alch_prices:
        item_id = str(item_info.get("id", ""))
        item_name = item_info.get("name", f"Item ID {item_id}")
        alch_value = item_info.get("high_alch_price")

        if not item_id or alch_value is None:
            continue

        current_market_price = live_prices.get(item_id, {}).get("low")
        if not current_market_price:
            continue

        profit = alch_value - current_market_price - nat_rune_cost
        if profit > 0:
            profitable_items.append({
                "name": item_name,
                "profit": profit,
                "buy_price": current_market_price,
                "alch_value": alch_value,
                "limit": item_info.get("buy_limit", "Unknown")
            })

    profitable_items.sort(key=lambda x: x["profit"], reverse=True)
    return profitable_items, nat_rune_cost



if __name__ == "__main__":
    print("==================================================")
    print("        OSRS DASHBOARD AUTOMATION ACTIVE          ")
    print("  This script will refresh prices every 5 minutes.")
    print("     Press CTRL+C in your terminal to stop it.    ")
    print("==================================================")
    
    try:
        while True:
            run_dashboard_pipeline()
            print(f"Waiting {INTERVAL_SECONDS // 60} minutes until next update...")
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nAutomation stopped safely.")
