import google.generativeai as genai
import os
import json
import time

def analyze_pdf(pdf_path):
    """
    Analyzes a PDF using Gemini 2.5 Flash Lite (API Key) to extract metadata and summary.
    """
    """
    Analyzes a PDF using Gemini 2.5 Flash Lite (API Key) to extract metadata and summary.
    """
    try:
        import streamlit as st
        api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
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
    # Using 2.5-pro as requested for higher quality
    model = genai.GenerativeModel("gemini-2.5-pro")

    prompt = """
    You are an expert academic researcher. Analyze the provided research paper PDF.
    
    **YOUR CONTEXT / MY RESEARCH TOPIC**:
    '마을교육공동체에 참여하는 중학교 교사들의 관계적 행위자성'
    (Please consider this topic when writing the 'Connection to My Research' section. BE VERY SPECIFIC.)

    **Task 1: Extract Metadata (JSON Format)**
    Extract the following fields into a JSON object key called "metadata".
    - Title: (String)
    - Authors: (String, comma-separated)
    - Year: (Integer)
    - Journal: (String)
    - Page: (String, Format: "Start-End", e.g. "1-20")
    - Keywords: (List of Strings)
    - Type: (String)
    - Volume_Issue: (String)
    - DOI: (String)
    
    **Task 2: Generate Summary (Markdown Format with Custom Tags)**
    Create a **HIGHLY DETAILED, COMPREHENSIVE** summary in Korean under the key "content".
    Do not summarize briefly. **Write in depth.**
    
    **CRITICAL RULES FOR CITATIONS**:
    - **EVERY QUOTE MUST HAVE A PAGE NUMBER.** Format: "(Quote)" (p.XX)
    - If you cannot find the page number, estimated it from the PDF page count.
    - Do not output (p.xx) as a placeholder. **FIND THE ACTUAL NUMBER.**
    
    [Template Start]
    ## 📌 연구 개요

    ### 연구 목적
    (Write a detailed paragraph explaining the specific purpose and background.) (p.XX)

    ### 연구 질문
    1. (Question 1) (p.XX)
    2. (Question 2) (p.XX)

    ### 연구의 필요성/문제의식
    (Explain why this research is needed in detail.) (p.XX)

    ---

    ## 📚 이론적 배경 (Detailed)

    ### 핵심 이론/프레임워크
    <callout icon="🔑">
    **[Theory Name]** (Author, Year)
    (Provide a detailed explanation of the theory and how it is applied here.) (p.XX)
    </callout>

    ### 주요 개념 정의
    - **[Concept 1]**: [Detailed Definition from text] (p.XX)
    - **[Concept 2]**: [Detailed Definition from text] (p.XX)

    ### 분석틀/연구 모형
    (Describe the analysis framework in detail.)
    - Component/Factor 1: ... (p.XX)
    - Component/Factor 2: ... (p.XX)

    ---

    ## 🔬 연구 방법

    ### 연구 설계
    - **연구 유형**: ...
    - **연구 전략**: ...

    ### 연구 참여자/대상
    (Detailed description of participants, table info, selection criteria.)

    ### 자료 수집 및 분석
    - (Method 1 & Procedure): ...
    - (Method 2 & Procedure): ...

    ---

    ## 🔍 연구 결과 (This is the most important section)

    ### 결과 개요
    (Provide a structured overview of the results.)

    ### 주요 발견 1: [Specific Theme Name]
    (Write a detailed paragraph explaining this finding. Do not be brief.) (p.XX)

    <callout icon="💬">
    "[Find a specific, meaningful direct quote from the text that supports this finding.]" (p.XX)
    </callout>

    ### 주요 발견 2: [Specific Theme Name]
    (Write a detailed paragraph explaining this finding.) (p.XX)
    
    <callout icon="💬">
    "[Find a specific, meaningful direct quote from the text that supports this finding.]" (p.XX)
    </callout>
    
    ### 주요 발견 3: [Specific Theme Name]
    (Write a detailed paragraph explaining this finding.) (p.XX)
    
    <callout icon="💬">
    "[Find a specific, meaningful direct quote from the text that supports this finding.]" (p.XX)
    </callout>

    ---

    ## 💡 논의 및 결론

    ### 결과 해석
    (How does the author interpret these results? Explain in depth.)

    ### 이론적/실천적 시사점
    1. (Implication 1 - Detailed) (p.XX)
    2. (Implication 2 - Detailed) (p.XX)
    3. (Implication 3 - Detailed) (p.XX)

    ### 연구의 한계 및 제언
    - (Limitation 1)
    - (Limitation 2)

    ---

    ## 🔗 나의 연구와의 연결 (Context: '마을교육공동체에 참여하는 중학교 교사들의 관계적 행위자성')

    ### 적용 가능성
    - (Analyze how the theories or findings here can be applied to middle school teachers' relational agency in village education communities.)

    ### 비판적 검토
    - **강점**: ...
    - **한계**: ...

    ### 메모
    (Insight)
    [Template End]

    **OUTPUT FORMAT**:
    Return a single valid JSON object:
    {
        "metadata": { ... },
        "content": "..."
    }
    """
    
    print(f"   ↳ 🧠 Generating content...")
    response = model.generate_content(
        [sample_file, prompt],
        generation_config={"response_mime_type": "application/json"}
    )
    
    # Cleanup Gemini File
    try:
        genai.delete_file(sample_file.name)
    except:
        pass
    
    # Clean up JSON string (remove markdown code blocks if present)
    json_str = response.text.strip()
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
        
    return json.loads(json_str.strip())
