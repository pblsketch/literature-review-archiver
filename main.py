import os
import glob
import shutil
from dotenv import load_dotenv
from utils.gemini_utils import analyze_pdf
from utils.notion_utils import create_notion_page
from utils.drive_utils import search_file

# Load environment variables
load_dotenv()

PROCESSED_DIR = "./papers/processed"

def main():
    print("="*50)
    print("📚 Literature Review Archiver (Antigravity)")
    print("="*50)
    print("ℹ️ Mode: Local PDF Analysis -> Notion (Metadata & Summary + Drive Link)")
    print("="*50)
    
    # 1. Environment Check
    if not os.environ.get("NOTION_KEY"):
        print("❌ Error: NOTION_KEY not found in .env file.")
        return
        
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY not found in .env file.")
        return

    # 2. Get Database ID
    database_id = os.environ.get("NOTION_DATABASE_ID")
    if not database_id:
        database_id = input("📂 Enter Notion Database ID: ").strip()
        if not database_id:
            print("❌ Database ID is required.")
            return

    # Ensure processed directory
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)

    # 3. Find PDFs (Recursive)
    # Search for all PDFs in papers and subfolders
    pdf_files = glob.glob(os.path.join("papers", "**", "*.pdf"), recursive=True)
    
    # Filter out files already in 'processed' folder to avoid re-processing if user moves them back or if glob is too greedy
    # Filter out files already in 'processed' folder to avoid re-processing
    pdf_files = [f for f in pdf_files if "processed" not in f.split(os.sep)]

    if not pdf_files:
        print("⚠️ No PDF files found in ./papers or its subfolders.")
        print("👉 Please check your folder structure.")
        return
        
    print(f"📄 Found {len(pdf_files)} PDF files to process.\n")

    # 4. Processing Loop
    for i, pdf_path in enumerate(pdf_files):
        file_name = os.path.basename(pdf_path)
        print(f"[{i+1}/{len(pdf_files)}] Processing: {file_name}")
        
        try:
            # Step A: Find in Google Drive
            print("   ↳ 🔍 Searching in Google Drive...")
            drive_link = search_file(file_name)
            if drive_link:
                print(f"     -> Found! Link embedded.")
            else:
                print(f"     -> Not found in Drive. Page will be created without link.")

            # Step B: Gemini Analysis (Local File)
            print("   ↳ 🧠 Analyzing with Gemini...")
            analysis_result = analyze_pdf(pdf_path)
            
            metadata = analysis_result.get('metadata', {})
            content_markdown = analysis_result.get('content', "")
            
            print(f"     -> Title: {metadata.get('Title')}")
            
            # Step C: Notion Creation (Metadata + Content + Drive Link)
            print("   ↳ 📝 Creating Notion Page...")
            create_notion_page(database_id, metadata, content_markdown, file_link=drive_link)
            
            # Step C: Move File
            target_path = os.path.join(PROCESSED_DIR, file_name)
            
            # Only move if the file is not already in the processed directory
            if os.path.abspath(pdf_path) != os.path.abspath(target_path):
                shutil.move(pdf_path, target_path)
                print("   ✅ Done! Moved to 'processed'.\n")
            else:
                print("   ✅ Done! (File already in 'processed').\n")
            
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}\n")
            import traceback
            traceback.print_exc()
            
    print("🎉 All tasks completed. check your Notion Database!")

if __name__ == "__main__":
    main()
