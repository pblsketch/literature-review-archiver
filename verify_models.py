from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("❌ API Key not found!")
    exit()

genai.configure(api_key=api_key)

print(f"🔑 API Key: {api_key[:5]}...{api_key[-3:]}")
print("📋 Listing available models...")

try:
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
