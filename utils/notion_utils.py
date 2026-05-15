from notion_client import Client
import os
import re

def parse_content_to_blocks(markdown_text):
    """
    Parses Markdown text with custom <aside> tags into Notion blocks.
    - <aside>...</aside> -> Callout
    - # -> Heading 1
    - ## -> Heading 2
    - Others -> Paragraph
    """
    blocks = []
    lines = markdown_text.split('\n')
    
    # State for processing
    in_aside = False
    aside_buffer = []
    current_icon = "💡"
    
    for line in lines:
        stripped = line.strip()
        
        # --- Custom <callout> tag processing ---
        # Regex to find <callout icon="X">Content</callout> (multiline capable)
        
        # Check for <callout ...> start
        callout_start_match = re.search(r'<callout icon=["\'](.+?)["\']>', stripped)
        if callout_start_match:
            in_aside = True
            current_icon = callout_start_match.group(1)
            
            # Content after the tag on the same line?
            content_after = stripped[callout_start_match.end():].strip()
            if content_after:
                aside_buffer.append(content_after)
                
            # If the line also contains </callout>, it's a one-liner
            if "</callout>" in stripped:
                # remove </callout> from the buffer's last element
                if aside_buffer:
                     aside_buffer[-1] = aside_buffer[-1].replace("</callout>", "").strip()
                 
                # Process immediately
                full_text = "\n".join(aside_buffer).strip()
                blocks.append({
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [{"type": "text", "text": {"content": full_text}}],
                        "icon": {"emoji": current_icon},
                        "color": "gray_background"
                    }
                })
                in_aside = False
                aside_buffer = []
                current_icon = "💡" # Reset
            continue

        # Check for end of </callout> if we are in one (and it wasn't a one-liner handled above)
        if in_aside and "</callout>" in stripped:
            content_before = stripped.replace("</callout>", "").strip()
            if content_before:
                aside_buffer.append(content_before)
            
            full_text = "\n".join(aside_buffer).strip()
            
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": full_text}}],
                    "icon": {"emoji": current_icon},
                    "color": "gray_background"
                }
            })
            
            in_aside = False
            aside_buffer = []
            current_icon = "💡"
            continue
            
        # Legacy <aside> support (convert to default callout)
        if "<aside>" in stripped:
             in_aside = True
             current_icon = "💡"
             content_after = stripped.replace("<aside>", "").strip()
             if content_after: aside_buffer.append(content_after)
             continue
             
        if "</aside>" in stripped:
             content_before = stripped.replace("</aside>", "").strip()
             if content_before: aside_buffer.append(content_before)
             
             full_text = "\n".join(aside_buffer).strip()
             
             # Detect icons in legacy aside text
             if "📌" in full_text: current_icon = "📌"
             elif "📖" in full_text: current_icon = "📖"
             elif "⭐" in full_text: current_icon = "⭐"
             elif "🔑" in full_text: current_icon = "🔑"
             elif "💬" in full_text: current_icon = "💬"
             
             # Remove icon from text if detected
             if current_icon in ["📌", "📖", "⭐", "🔑", "💬"]:
                 full_text = full_text.replace(current_icon, "").strip()

             blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": full_text}}],
                    "icon": {"emoji": current_icon},
                    "color": "gray_background"
                }
            })
             in_aside = False
             aside_buffer = []
             continue
             
        if in_aside:
            aside_buffer.append(stripped)
            continue
            
        # --- Normal Markdown Processing ---
        if not stripped:
            continue
            
        if stripped.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"type": "text", "text": {"content": stripped[2:]}}]}
            })
        elif stripped.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": stripped[3:]}}]}
            })
        elif stripped.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": stripped[4:]}}]}
            })
        elif stripped.startswith("- "):
             blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": stripped[2:]}}]}
            })
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": stripped}}]}
            })
            
    return blocks

def create_notion_page(database_id, metadata, content_markdown, file_link):
    try:
        import streamlit as st
        try:
             notion_key = st.secrets.get("NOTION_KEY") or os.environ.get("NOTION_KEY")
        except (FileNotFoundError, Exception): # Fallback if secrets.toml is missing
             notion_key = os.environ.get("NOTION_KEY")
    except ImportError:
        notion_key = os.environ.get("NOTION_KEY")

    client = Client(auth=notion_key)
    
    # Retrieve Database Schema to validate properties
    valid_properties = []
    try:
        db_info = client.databases.retrieve(database_id)
        valid_properties = list(db_info.get("properties", {}).keys())
        print(f"🔎 DEBUG: Real Schema Keys from Notion: {valid_properties}")
    except Exception as e:
        print(f"⚠️ Failed to retrieve database schema: {e}")
        # Fallback: Hardcode properties based on User's explicit list (Capitalized)
        valid_properties = [
            'Name', 'Authors', 'Collections', 'Tags', 'URL', '읽음 상태', 
            'Volume', 'Issue', 'Pages', 'Publication', 'DOI', '인용 여부', 'Date'
        ]
        print(f"🔎 DEBUG: Using Fallback Schema: {valid_properties}")

    # Helper: Create case-insensitive map
    real_key_map = {k.lower().strip(): k for k in valid_properties}

    # Helper to clean/check keys
    final_props = {}
    
    def add_prop(key_candidates, value_dict, is_required=False):
        """
        Tries to find a valid key from candidates (Case Insensitive).
        """
        if not real_key_map:
             if is_required:
                 # If we have no schema info, simply use the first candidate (Capitalized usually)
                 final_props[key_candidates[0]] = value_dict
             return

        for key in key_candidates:
            clean_key = key.lower().strip()
            if clean_key in real_key_map:
                real_key = real_key_map[clean_key]
                final_props[real_key] = value_dict
                return
        
        # If required and no match found, force it (might error, but better than missing title)
        if is_required:
             final_props[key_candidates[0]] = value_dict

    # --- Construct Properties ---
    
    # Name (REQUIRED)
    add_prop(['Name', 'name', '논문 제목', 'Title'], {'title': [{'text': {'content': metadata.get('Title', 'Untitled')}}]}, is_required=True)
    
    # Authors
    if metadata.get('Authors'):
        add_prop(['Authors', 'authors', 'Author', '저자'], {'rich_text': [{'text': {'content': str(metadata['Authors'])}}]})
        
    # Date (Number)
    if metadata.get('Year'):
        add_prop(['Date', 'date', 'Year', '발행연도'], {'number': int(metadata['Year'])})
        
    # Publication
    if metadata.get('Journal'):
        add_prop(['Publication', 'publication', 'Journal', '학술지명/출처'], {'rich_text': [{'text': {'content': str(metadata['Journal'])}}]})
        
    # Pages
    if metadata.get('Page'):
        add_prop(['Pages', 'pages', 'Page', '페이지'], {'rich_text': [{'text': {'content': str(metadata['Page'])}}]})

    # Tags (Multi-select)
    if metadata.get('Keywords'):
        tags = []
        for k in metadata['Keywords']:
            clean_tag = k.replace(',', '').strip()
            if clean_tag:
                tags.append({'name': clean_tag})
        if tags:
            add_prop(['Tags', 'tags', 'Keywords', '핵심 키워드'], {'multi_select': tags})
        
    # Collections (Multi-select observed in screenshot)
    if metadata.get('Type'):
        # Assuming Multi-select based on user screenshot
        add_prop(['Collections', 'collections', 'Type', '유형'], {'multi_select': [{'name': metadata['Type']}]})
    
    # Status
    add_prop(['읽음 상태', 'Status', 'status'], {'status': {'name': '읽을 예정'}}) 
    
    # Volume / Issue
    vol_issue = metadata.get('Volume_Issue', '')
    if vol_issue:
        match = re.match(r"(\d+)\s*\((.+)\)", str(vol_issue))
        if match:
             add_prop(['Volume', 'volume', '권'], {'rich_text': [{'text': {'content': match.group(1)}}]})
             add_prop(['Issue', 'issue', '호'], {'rich_text': [{'text': {'content': match.group(2)}}]})
        else:
             add_prop(['Volume', 'volume', '권'], {'rich_text': [{'text': {'content': str(vol_issue)}}]})
             # Try to add volume_issue to either field if only one exists or fallback
             # But here we just keep it simple.

    # DOI (Strictly to DOI column, Link/URL type)
    if metadata.get('DOI'):
        add_prop(['DOI', 'doi'], {'url': str(metadata['DOI'])})
        
    # Files / URL (For PDF Link)
    if file_link:
        # 1. Try 'Files' (File type)
        file_prop_exists = any(k in real_key_map for k in ['files', 'file', '파일 첨부', 'pdf'])
        
        if file_prop_exists:
             add_prop(['Files', 'files', 'File', '파일 첨부', 'PDF'], {
                'files': [{
                    'type': 'external',
                    'name': 'PDF Link',
                    'external': {'url': file_link}
                }]
            })
        else:
            # 2. Fallback to 'URL' (Url type)
            add_prop(['URL', 'url', 'Link'], {'url': file_link})
        
    # Parse Body
    children = parse_content_to_blocks(content_markdown)
    
    print(f"🔎 DEBUG: Final Properties to Send: {list(final_props.keys())}")
    
    try:
        client.pages.create(
            parent={'database_id': database_id},
            properties=final_props,
            children=children
        )
    except Exception as e:
        print(f"❌ Notion API Error: {str(e)}")
        raise e
