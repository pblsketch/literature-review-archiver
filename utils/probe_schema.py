from notion_client import Client
import os
from dotenv import load_dotenv
import json

load_dotenv()

notion = Client(auth=os.environ["NOTION_KEY"])
database_id = os.environ["NOTION_DATABASE_ID"]

print("🕵️ Probing Database Schema by creating an Empty Page...")

try:
    # 1. Create Empty Page
    page = notion.pages.create(parent={"database_id": database_id}, properties={})
    print(f"✅ Created Probe Page ID: {page['id']}")
    
    # 2. Inspect Properties
    print("📋 Discovered Properties:")
    real_props = page['properties']
    for key, val in real_props.items():
        print(f"   - {key} ({val['type']})")
        
    # 3. Archive (Delete) Page
    notion.pages.update(page_id=page['id'], archived=True)
    print("🗑️ Probe Page Archived.")

except Exception as e:
    print(f"❌ Probe Failed: {e}")
