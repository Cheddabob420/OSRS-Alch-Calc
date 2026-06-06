#!/home/pi/.venv/bin/python3

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

def calculate_processing_profits(live_prices):
    """
    Takes the live prices data block and runs a recipe-based 
    margin analysis for cleaning herbs and making unfinished potions.
    """
    if not live_prices:
        return []

    # Map out recipes explicitly by Item ID (No name searching errors!)
    recipes = [
        # --- HERB CLEANING RECIPES ---
        {"name": "Clean Ranarr Weed", "input_id": "207", "output_id": "257", "type": "Herb Cleaning"},
        {"name": "Clean Avantoe", "input_id": "211", "output_id": "261", "type": "Herb Cleaning"},
        {"name": "Clean Toadflax", "input_id": "3049", "output_id": "2998", "type": "Herb Cleaning"},
        {"name": "Clean Snapdragon", "input_id": "3051", "output_id": "3000", "type": "Herb Cleaning"},
        {"name": "Clean Torstol", "input_id": "219", "output_id": "269", "type": "Herb Cleaning"},
        {"name": "Clean Kwuarm", "input_id": "213", "output_id": "263", "type": "Herb Cleaning"},
        
        # --- UNFINISHED POTION RECIPES --- (Input: Clean Herb + Vial of Water [227])
        {"name": "Ranarr unf pot", "input_id": "257", "output_id": "91", "type": "Unf Potion", "needs_vial": True},
        {"name": "Toadflax unf pot", "input_id": "2998", "output_id": "3002", "type": "Unf Potion", "needs_vial": True},
        {"name": "Snapdragon unf pot", "input_id": "3000", "output_id": "3004", "type": "Unf Potion", "needs_vial": True},
        {"name": "Avantoe unf pot", "input_id": "261", "output_id": "97", "type": "Unf Potion", "needs_vial": True},
        {"name": "Torstol unf pot", "input_id": "269", "output_id": "111", "type": "Unf Potion", "needs_vial": True}
    ]

    VIAL_OF_WATER_ID = "227"
    # Buy vials instantly (high)
    vial_cost = live_prices.get(VIAL_OF_WATER_ID, {}).get("high", 3) 

    processing_results = []

    for recipe in recipes:
        # Get input cost (instant buy = high)
        input_cost = live_prices.get(recipe["input_id"], {}).get("high")
        # Get output revenue (instant sell = low)
        output_revenue = live_prices.get(recipe["output_id"], {}).get("low")

        # Skip if either item doesn't have active live trading data right now
        if not input_cost or not output_revenue:
            continue

        # Adjust cost if it's an unfinished potion requiring a vial of water
        total_input_cost = input_cost
        if recipe.get("needs_vial"):
            total_input_cost += vial_cost

        # Calculate pure margin
        profit = output_revenue - total_input_cost

        processing_results.append({
            "name": recipe["name"],
            "type": recipe["type"],
            "profit": profit,
            "buy_price": total_input_cost,
            "sell_price": output_revenue
        })

    # Sort processing margins from highest to lowest profit
    processing_results.sort(key=lambda x: x["profit"], reverse=True)
    return processing_results


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
