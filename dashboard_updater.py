from datetime import datetime
import json
import alch_engine

OUTPUT_JSON_FILE = "/home/dietpi/osrs/live_alchs.json" # Use absolute paths on the Pi

def run_dashboard_pipeline():
    base_items = alch_engine.get_item_data()
    if not base_items:
        return
        
    profitable_list, nature_rune_cost = alch_engine.find_alch_opportunities(base_items)
    
    dashboard_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nature_rune_cost": nature_rune_cost,
        "items": profitable_list
    }
    
    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_dashboard_pipeline()
