import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

print("🔧 RAG ストア構築スクリプト開始")

# ---- APIキー読込 ----
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ GEMINI_API_KEY が見つかりません。.env または GitHub Secrets を確認してください。")

client = genai.Client(api_key=api_key)

# ---- ストア作成 ----
print("📁 RAG ファイル検索ストアを作成中...")
store = client.file_stores.create()
print(f"✅ ストア作成成功: {store.name}")

# ---- ドキュメントのフォルダ ----
DOC_DIR = "gemini_api_docs_txt"

if not os.path.exists(DOC_DIR):
    raise ValueError(f"❌ {DOC_DIR} が存在しません。HTML→TXT の変換が実行されていません。")

# ---- ファイル一覧 ----
files = [f for f in os.listdir(DOC_DIR) if f.endswith(".txt")]
print(f"📄 アップロードするファイル数: {len(files)}")

if not files:
    raise ValueError("❌ アップロード対象の TXT ドキュメントが 0 件です。")

# ---- アップロード ----
for f in files:
    path = os.path.join(DOC_DIR, f)
    print(f"⬆️ アップロード中: {f}")

    uploaded = client.files.upload(
        file=path,
        file_store_id=store.name
    )

print("🎉 すべてのファイルアップロードが完了")

# ---- ストア名を保存 ----
with open("setup_rag_store_file_search_store_name.txt", "w", encoding="utf-8") as fw:
    fw.write(store.name)

print(f"📌 ストア名を書き込みました: {store.name}")
print("✅ RAG ストア構築が完了しました！")

