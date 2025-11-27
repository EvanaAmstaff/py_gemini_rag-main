# setup_rag_store.py (【最終修正版】)
import os
import time
from google import genai
from dotenv import load_dotenv

# --- .envファイルから環境変数を読み込む ---
load_dotenv()

# --- 環境変数からAPIキーを取得 ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("APIキーが.envファイルに設定されていません。'GEMINI_API_KEY=...'と記述してください。")

# --- Clientオブジェクトを作成 ---
client = genai.Client(api_key=api_key) 
doc_directorys = ["gas_docs_txt","gemini_api_docs_txt"]
#doc_directorys = ["gas","gemini"]

# --- 1. ファイル検索ストアの作成 ---
print("ファイル検索ストアを作成しています...")
file_search_store = client.file_search_stores.create(
    config={'display_name': 'GAS Documentation RAG Store (new SDK)'}
)

# --- 2. ディレクトリ内の全テキストファイルをアップロード ---
print(f"'{doc_directorys}' ディレクトリからファイルのアップロードを開始します...")
for doc_directory in doc_directorys:
    for filename in os.listdir(doc_directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(doc_directory, filename)
            print(f"  - アップロード中: {filename}")
            
            # 最初のアップロード操作を開始
            operation = client.file_search_stores.upload_to_file_search_store(
                file=file_path,
                file_search_store_name=file_search_store.name,
                config={'display_name': filename}
            )
            
            # ▼▼▼【ここからが修正箇所】▼▼▼

            # 操作が完了するまでループ (公式ドキュメントに準拠したシンプルな形式)
            while not operation.done:
                print("    - 処理中...")
                time.sleep(5)
                
                # operationオブジェクト自体を渡して、最新の状態を取得する
                operation = client.operations.get(operation)

            # ▲▲▲【ここまでが修正箇所】▲▲▲

print("\n✅ すべてのファイルのアップロードとインデックス作成が完了しました。")
print("\n🎉 RAGシステムの準備が完了しました！")
print("以下のストア名（ID）をコピーして、質問用スクリプトに貼り付けてください。")
print("--------------------------------------------------")
print(file_search_store.name)
print("--------------------------------------------------")
# ファイルを保存
file_path = "setup_rag_store_file_search_store_name.txt"
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(file_search_store.name)
print(f"  保存先: {file_path}")