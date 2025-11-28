import google.generativeai as genai
import time
import magic   # ファイルMIME判定
import os

# -------------------------------
# 1. Gemini APIキー設定
# -------------------------------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# -------------------------------
# 2. ファイルアップロード関数
# -------------------------------
def upload_file_to_gemini(filepath: str):
    print(f"📤 Gemini にファイルをアップロード中: {filepath}")

    mime = magic.from_file(filepath, mime=True)

    uploaded_file = genai.files.upload(
        file=filepath,
        mime_type=mime
    )

    print(f"✅ アップロード完了: file_id={uploaded_file.file_id}")
    return uploaded_file


# -------------------------------
# 3. Q&A（ファイル + テキストプロンプト）
# -------------------------------
def ask_question_with_file(gemini_file, question: str):

    model = genai.GenerativeModel("gemini-2.0-flash")

    print("🤖 回答生成中...")

    response = model.generate_content(
        [
            gemini_file,
            question
        ]
    )

    return response.text


# -------------------------------
# 4. メイン処理
# -------------------------------
if __name__ == "__main__":
    filepath = input("解析したいファイルのパスを入力してください: ")

    file_obj = upload_file_to_gemini(filepath)

    print("\n--- ファイルがアップロードされました！ ---")
    print("質問を入力してください（Enter で終了）")

    while True:
        question = input(">> ")
        if question.strip() == "":
            print("終了します。")
            break

        answer = ask_question_with_file(file_obj, question)
        print("\n--- 回答 ---")
        print(answer)
        print("\n")
