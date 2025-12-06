from notion_client import Client
import os
from dotenv import load_dotenv
import json

load_dotenv()

notion = Client(auth=os.environ["NOTION_KEY"])
database_id = os.environ["NOTION_DATABASE_ID"]

try:
    print("🔎 Searching for accessible databases (no filter)...")
    results = notion.search().get("results")
    
    # Filter manually for databases
    results = [r for r in results if r['object'] == 'database']
    
    if not results:
        print("❌ No databases found. Please ensure the integration is added to the database page.")
    
    for db in results:
        print(f"\n📂 Database Found: {db['title'][0]['plain_text'] if db['title'] else 'Untitled'}")
        print(f"   ID: {db['id']}")
        if os.environ["NOTION_DATABASE_ID"].replace("-", "") in db['id'].replace("-", ""):
             print("   ✅ MATCHES YOUR ID!")
        
        if 'properties' in db:
            print("   Properties:")
            for prop_name, prop_data in db['properties'].items():
                print(f"    - '{prop_name}': {prop_data['type']}")
        else:
            print("   ❌ Key 'properties' missing in search result too.")

except Exception as e:
    print(f"Error searching: {e}")
