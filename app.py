import streamlit as st
import os
import shutil
import tempfile
from dotenv import load_dotenv
from utils.gemini_utils import analyze_pdf
from utils.notion_utils import create_notion_page
from utils.drive_utils import search_file

# Set page config
st.set_page_config(
    page_title="Literature Review Archiver",
    page_icon="📚",
    layout="wide"
)

# Load environment variables
load_dotenv()

def main():
    st.title("📚 Literature Review Archiver")
    st.markdown("---")
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys Check
        gemini_key = os.environ.get("GEMINI_API_KEY")
        notion_key = os.environ.get("NOTION_KEY")
        
        if gemini_key:
            st.success("✅ GEMINI_API_KEY found")
        else:
            st.error("❌ GEMINI_API_KEY missing")
            
        if notion_key:
            st.success("✅ NOTION_KEY found")
        else:
            st.error("❌ NOTION_KEY missing")
            
        st.markdown("---")
        
        # Database ID Input
        database_id_env = os.environ.get("NOTION_DATABASE_ID")
        database_id = st.text_input(
            "Notion Database ID", 
            value=database_id_env if database_id_env else "",
            type="password"
        )
        
        if not database_id:
            st.warning("⚠️ Please enter a Notion Database ID to proceed.")
            
    # Main Content
    st.info("ℹ️ Mode: Upload PDF Analysis -> Notion (Metadata & Summary + Drive Link)")
    
    if not gemini_key or not notion_key or not database_id:
        st.error("Please configure the API keys and Database ID in the sidebar/env file.")
        st.stop()
        
    # File Uploader
    uploaded_files = st.file_uploader(
        "Upload PDF files", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"📄 **{len(uploaded_files)} files selected**")
        
        if st.button("🚀 Start Processing", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            logs = st.expander("Processing Logs", expanded=True)
            
            for i, uploaded_file in enumerate(uploaded_files):
                file_name = uploaded_file.name
                current_progress = (i) / len(uploaded_files)
                progress_bar.progress(current_progress)
                status_text.text(f"Processing {i+1}/{len(uploaded_files)}: {file_name}")
                
                with logs:
                    st.write(f"**[{i+1}/{len(uploaded_files)}] Processing:** `{file_name}`")
                    
                    try:
                        # 1. Save to temporary file for processing
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                            
                        # Step A: Find in Google Drive
                        st.write("↳ 🔍 Searching in Google Drive...")
                        drive_link = search_file(file_name)
                        if drive_link:
                            st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;✅ Found! Link embedded: [Open]({drive_link})")
                        else:
                            st.write("&nbsp;&nbsp;&nbsp;&nbsp;⚠️ Not found in Drive.")
                            
                        # Step B: Gemini Analysis
                        st.write("↳ 🧠 Analyzing with Gemini...")
                        analysis_result = analyze_pdf(tmp_path)
                        
                        metadata = analysis_result.get('metadata', {})
                        content_markdown = analysis_result.get('content', "")
                        
                        st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;✅ Analyzed: **{metadata.get('Title', 'Untitled')}**")
                        
                        # Step C: Notion Creation
                        st.write("↳ 📝 Creating Notion Page...")
                        create_notion_page(database_id, metadata, content_markdown, file_link=drive_link)
                        st.write("&nbsp;&nbsp;&nbsp;&nbsp;✅ Notion Page Created!")
                        
                        # Cleanup temp file
                        os.unlink(tmp_path)
                        
                    except Exception as e:
                        st.error(f"❌ Failed to process {file_name}: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                        
                st.divider()
                
            progress_bar.progress(1.0)
            status_text.text("Done!")
            st.success("🎉 All files processed successfully!")
            st.balloons()

if __name__ == "__main__":
    main()
