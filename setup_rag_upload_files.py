# setup_rag_upload_files.py
import os
from google import genai
from dotenv import load_dotenv
import json

print("🔧 RAG ファイルアップロードスクリプト開始")

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY が設定されていません")

client = genai.Client(api_key=api_key)

# アップロード対象フォルダ
TARGET_DIR = "./gas_docs_txt"

file_ids = []

print("📁 ファイルアップロード開始...")

for filename in os.listdir(TARGET_DIR):
    path = os.path.join(TARGET_DIR, filename)
    if not os.path.isfile(path):
        continue

    print(f"  ⏫ Uploading: {filename}")

    uploaded = client.files.upload(
        file=path,
        display_name=filename
    )

    file_ids.append(uploaded.name)

print("✅ すべてのファイルをアップロード完了！")

# file_id を保存して query_rag.py から使えるようにする
with open("uploaded_file_ids.json", "w", encoding="utf-8") as f:
    json.dump({"file_ids": file_ids}, f, ensure_ascii=False, indent=2)

print("💾 uploaded_file_ids.json に保存しました")
print("🎉 RAG アップロード作業 完了!")
