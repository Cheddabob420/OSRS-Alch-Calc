import requests
import json
import os
import subprocess
import re


headers = {
    'User-Agent': 'OsrsItemDataFetcher/1.0 (Email: cogygibson420gmail.com)'
}

mapping = 'https://prices.runescape.wiki/api/v1/osrs/mapping'
pricing = 'https://prices.runescape.wiki/api/v1/osrs/latest'



def make_item_json(json_file):
    response = requests.get(mapping, headers=headers)
    if response.status_code == 200:
        if response.text.strip().startswith("<!DOCTYPE html>"):
            print("Error: Received HTML content instead of JSON. Check the URL and try again.")
        else:
            raw_data = response.json()
            cleaned_items = []
            for item in raw_data:
                extracted_info ={
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "high_alch_price": item.get("highalch", 0),
                    "buy_limit": item.get("limit", 0)
                }
                cleaned_items.append(extracted_info)
                
            with open(json_file, "w") as f:
                json.dump(cleaned_items, f, indent=4)
            print(f"Data successfully saved to {json_file}")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        
def find_id_by_name(json_file_path, search_name):
    # Ensure the file exists before running the command
    if not os.path.exists(json_file_path):
        return "Error: File not found."

    try:
        exact_search = f'"{search_name}"'
        result = subprocess.run(
            ['grep', '-B', '1', '-i', exact_search, json_file_path],
            capture_output=True,
            text=True,
            check=True
        )
        grep_output = result.stdout.strip()
        if not grep_output:
            return "No match found."
            
        id_match = re.search(r'"id"\s*:\s*(\d+)', grep_output)
        
        if id_match:
            return id_match.group(1)
        else:
            return "Match found, but couldn't parse the ID number above it."

    except subprocess.CalledProcessError:
        return "No match found in the file."
    except Exception as e:
        return f"An error occurred: {e}"
    
def find_alch_opportunities(alch_prices):
    if not alch_prices:
        return [], 124

    print("Fetching live Grand Exchange margins...")
    try:
        response = requests.get(pricing, headers=headers)
        response.raise_for_status()
        live_prices = response.json().get("data", {})
    except requests.exceptions.RequestException as e:
        print(f"Error fetching live prices from API: {e}")
        return [], 124

    nat_rune_data = live_prices.get("124", {})
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

def item_searcher():
    json_file = input("Enter the name of the JSON file that contains the item data (e.g., osrs_items.json): ").strip()
    if not os.path.exists(json_file):
        make_item_json(json_file)
    else:
        target_file = json_file
        user_input = input("Enter the name to search for: ")
        print(f"Searching for '{user_input}'...")
        result_id = find_id_by_name(target_file, user_input)
        print(f"Result: {result_id}")


if __name__ == "__main__":
   item_searcher()
