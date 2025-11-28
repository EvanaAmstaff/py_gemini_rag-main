import os
from google import genai

# ---------------------------
# API キー読み込み
# ---------------------------
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ APIキーが見つかりません。環境変数に GEMINI_API_KEY または GOOGLE_API_KEY を設定してください。")
    exit()

client = genai.Client(api_key=api_key)

# ---------------------------
# RAG 文書読み込み
# ---------------------------
DOC_PATH = "gas_docs_txt/gas_all.txt"

if not os.path.exists(DOC_PATH):
    print(f"❌ RAG ドキュメントが見つかりません: {DOC_PATH}")
    print("HTML → TXT 変換（local_html2text.py）を実行しましたか？")
    exit()

with open(DOC_PATH, "r", encoding="utf-8") as f:
    GAS_TEXT_DATA = f.read()


# ---------------------------
# RAG 回答生成
# ---------------------------
def answer_with_rag(question: str) -> str:
    prompt = f"""
あなたは Google Apps Script 専門アシスタントです。

以下は GAS の公式ドキュメントから自動生成されたテキストデータです。
これを参考にして、ユーザーの質問にできるだけ正確に答えてください。

【ドキュメント】
{GAS_TEXT_DATA}

【質問】
{question}

【回答】
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text


# ---------------------------
# メイン処理（API 使用は1回のみ）
# ---------------------------
if __name__ == "__main__":
    print("質問を入力してください（Enterのみで終了）:")

    while True:
        question = input(">> ")

        if question.strip() == "":
            print("終了します。")
            break

        print("\n--- 回答 ---")

        try:
            answer = answer_with_rag(question)
            print(answer)
        except Exception as e:
            print("❌ エラー:", e)
