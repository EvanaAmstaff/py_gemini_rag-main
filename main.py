import os
import time
import google.generativeai as genai

# APIキー
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

def ask_gemini(question):
    """Gemini に質問して回答を返す"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"Error: {e}"

def main():
    input_file = "questions.txt"
    output_file = "output/answers.txt"

    os.makedirs("output", exist_ok=True)

    if not os.path.exists(input_file):
        print("questions.txt がありません")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        questions = [q.strip() for q in f.readlines() if q.strip()]

    with open(output_file, "w", encoding="utf-8") as out:
        for q in questions:
            print(f"質問: {q}")
            answer = ask_gemini(q)
            out.write(f"質問: {q}\n回答: {answer}\n\n")
            time.sleep(1)

    print(f"完了: {output_file} に保存されました")

if __name__ == "__main__":
    main()
