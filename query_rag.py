# query_rag.py
import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

STORE_DIR = "rag_store"

def main():
    question = input("質問を入力してください: ")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    vectordb = FAISS.load_local(STORE_DIR, embeddings, allow_dangerous_deserialization=True)

    docs = vectordb.similarity_search(question, k=3)

    context = "\n\n".join([d.page_content for d in docs])

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-thinking-exp",
        temperature=0.2
    )

    prompt = f"""
あなたは優秀なアシスタントです。
以下の「コンテキスト」を必ず参照して質問に答えてください。

--- コンテキスト ---
{context}

--- 質問 ---
{question}

--- 回答 ---
"""

    answer = llm.invoke(prompt)
    print("\n--- 回答 ---")
    print(answer.content)

if __name__ == "__main__":
    main()
