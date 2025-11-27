# setup_rag_store.py
import os
import glob
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

DATA_DIR = "data"
STORE_DIR = "rag_store"

def load_documents():
    docs = []
    for file in glob.glob(f"{DATA_DIR}/**/*.*", recursive=True):
        if file.endswith(".md") or file.endswith(".txt"):
            with open(file, "r", encoding="utf-8") as f:
                docs.append(f.read())
    return docs

def main():
    print("🔧 RAG ストア構築スクリプト開始")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ 環境変数 GEMINI_API_KEY が設定されていません")

    print("📄 文書読み込み中...")
    documents = load_documents()
    if not documents:
        raise ValueError(f"❌ {DATA_DIR} に文書がありません")

    print("✂️ 文書スプリット中...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.create_documents(documents)

    print("🧠 Embedding 生成中...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    print("📁 FAISS ベクトルストア作成...")
    vector_store = FAISS.from_documents(chunks, embeddings)

    Path(STORE_DIR).mkdir(exist_ok=True)
    vector_store.save_local(STORE_DIR)

    print("✅ RAG ストア構築完了！")

if __name__ == "__main__":
    main()
