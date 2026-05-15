import google.generativeai as genai
import os
import time
import json
import re

def analyze_pdf(pdf_path):
    """
    Analyzes a PDF using Gemini 2.5 Flash Lite (API Key) to extract metadata and summary.
    """
    try:
        import streamlit as st
        try:
            api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        except (FileNotFoundError, Exception): # Fallback if secrets.toml is missing
            api_key = os.environ.get("GEMINI_API_KEY")
    except ImportError:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment or secrets.")
        
    genai.configure(api_key=api_key)
    
    # Upload file to Gemini File API (Temporary storage for analysis)
    print(f"   ↳ 📤 Uploading to Gemini File API...")
    sample_file = genai.upload_file(path=pdf_path, display_name=os.path.basename(pdf_path))
    
    # Wait for processing
    while sample_file.state.name == "PROCESSING":
        time.sleep(1)
        sample_file = genai.get_file(sample_file.name)
        
    if sample_file.state.name == "FAILED":
        raise ValueError("Gemini failed to process the PDF.")

    # Model Setup
    # Using gemini-2.5-pro as requested by user
    model = genai.GenerativeModel("gemini-2.5-pro")

    prompt = """
    You are an expert academic researcher. Analyze the provided research paper PDF.
    
    **YOUR CONTEXT / MY RESEARCH TOPIC**:
    '마을교육공동체에 참여하는 중학교 교사들의 관계적 행위자성'
    (Please consider this topic when writing the 'Connection to My Research' section. BE VERY SPECIFIC.)

    **INSTRUCTIONS**:
    1. First, provide the **Metadata** in a JSON code block.
    2. Second, provide the **Summary** in standard Markdown format.
    
    ---
    
    ### PART 1: METADATA (JSON)
    Output the following fields in a `json` code block.
    - Title: (String)
    - Authors: (String, comma-separated)
    - Year: (Integer)
    - Journal: (String)
    - Page: (String, Format: "Start-End", e.g. "1-20")
    - Keywords: (List of Strings)
    - Type: (String)
    - Volume_Issue: (String)
    - DOI: (String)

    Example format:
    ```json
    {
        "Title": "Paper Title",
        "Year": 2023,
        ...
    }
    ```
    
    ---
    
    ### PART 2: SUMMARY (Markdown)
    **DO NOT put this summary inside the JSON.** Write it as plain Markdown text after the JSON block.
    
    **Content Requirements**:
    - **HIGHLY DETAILED, COMPREHENSIVE** summary in Korean.
    - **CITATIONS**: Every quote/finding must have a page number (p.XX).
    
    [Template Start]
    ## 📌 연구 개요

    ### 연구 목적
    (Detailed paragraph) (p.XX)

    ### 연구 질문
    1. ...
    2. ...

    ### 연구의 필요성/문제의식
    ...

    ---

    ## 📚 이론적 배경 (Detailed)
    ...
    <callout icon="🔑">
    **[Theory Name]** 
    ...
    </callout>

    ...

    ## 🔍 연구 결과 (Most Important)
    ...
    <callout icon="💬">
    "[Quote]" (p.XX)
    </callout>
    ...

    ## 💡 논의 및 결론
    ...

    ## 🔗 나의 연구와의 연결 (Context: '마을교육공동체에 참여하는 중학교 교사들의 관계적 행위자성')
    ...
    
    [Template End]
    """
    
    print(f"   ↳ 🧠 Generating content (Metadata + Markdown)...")
    
    # Generate TEXT (not forced JSON) to allow mixed output
    response = model.generate_content(
        [sample_file, prompt]
    )
    
    # Cleanup Gemini File
    try:
        genai.delete_file(sample_file.name)
    except:
        pass
    
    full_text = response.text
    
    # Parse Metadata (JSON Block)
    metadata = {}
    try:
        import re
        import json
        # Find JSON block
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", full_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            metadata = json.loads(json_str)
        else:
            # Fallback: exact match for first { ... } pair?
            # Or maybe the model didn't use code blocks.
            start = full_text.find('{')
            end = full_text.find('}') + 1
            if start != -1 and end != -1:
                 metadata = json.loads(full_text[start:end])
    except Exception as e:
        print(f"⚠️ Failed to parse Metadata JSON: {e}")
        print(f"RAW TEXT START: {full_text[:500]}")
    
    # Parse Content (Markdown)
    # The content is everything NOT in the JSON block, effectively. 
    # Or simplified: Everything after the JSON block, or just the whole text if we want to be lazy (but we want to strip the JSON).
    
    content_markdown = full_text
    # Remove the JSON part from content to avoid duplication in Notion page
    if 'json_match' in locals() and json_match:
        content_markdown = full_text.replace(json_match.group(0), "").strip()
    
    # Optional: If there's unrelated text at start, we might clean it.
    # Looking for "[Template Start]" or "## 📌 연구 개요"
    header_start = content_markdown.find("## 📌 연구 개요")
    if header_start != -1:
        content_markdown = content_markdown[header_start:]
        
    return {
        "metadata": metadata,
        "content": content_markdown
    }
