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
        notion_key = st.secrets.get("NOTION_KEY") or os.environ.get("NOTION_KEY")
    except ImportError:
        notion_key = os.environ.get("NOTION_KEY")

    client = Client(auth=notion_key)
    
    # Map Properties (Using correct Korean Schema)
    props = {}
    
    # Title -> 논문 제목
    props['논문 제목'] = {'title': [{'text': {'content': metadata.get('Title', 'Untitled')}}]}
    
    # Authors -> 저자
    if metadata.get('Authors'):
        props['저자'] = {'rich_text': [{'text': {'content': str(metadata['Authors'])}}]}
        
    # Year -> 발행연도
    if metadata.get('Year'):
        props['발행연도'] = {'number': int(metadata['Year'])}
        
    # Journal -> 학술지명/출처
    if metadata.get('Journal'):
        props['학술지명/출처'] = {'rich_text': [{'text': {'content': str(metadata['Journal'])}}]}
        
    # Page -> 페이지
    if metadata.get('Page'):
        # Store page range as text (e.g., "29-45")
        props['페이지'] = {'rich_text': [{'text': {'content': str(metadata['Page'])}}]}

        
    # Keywords -> 핵심 키워드
    if metadata.get('Keywords'):
        props['핵심 키워드'] = {'multi_select': [{'name': k.replace(',', '')} for k in metadata['Keywords']]}
        
    # Type -> 유형
    if metadata.get('Type'):
        props['유형'] = {'select': {'name': metadata['Type']}}
        
    # Status -> 읽음 상태
    props['읽음 상태'] = {'status': {'name': '읽을 예정'}}
    
    # Volume_Issue -> 권(호)
    if metadata.get('Volume_Issue'):
        props['권(호)'] = {'rich_text': [{'text': {'content': str(metadata['Volume_Issue'])}}]}
        
    # DOI -> URL/DOI
    if metadata.get('DOI'):
        props['URL/DOI'] = {'url': str(metadata['DOI'])}
        
    # File -> 파일 첨부 (External)
    if file_link:
        props['파일 첨부'] = {
            'files': [{
                'type': 'external',
                'name': 'PDF Link',
                'external': {'url': file_link}
            }]
        }
        
    # Parse Body
    children = parse_content_to_blocks(content_markdown)
    
     # print("Creating Notion Page...")
    try:
        client.pages.create(
            parent={'database_id': database_id},
            properties=props,
            children=children
        )
    except Exception as e:
        print(f"❌ Notion API Error: {str(e)}")
        raise e
