import os
from google import genai

def load_questions(path="src/questions.txt"):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY が設定されていません")

    client = genai.Client(api_key=api_key)
    model = "gemini-2.0-flash"

    questions = load_questions()
    if not questions:
        print("質問がありません（questions.txt を確認）")
        return

    print("=== Auto QA Results ===")
    for q in questions:
        print(f"\nQ: {q}")

        try:
            resp = client.models.generate_content(model=model, contents=q)
            print(f"A: {resp.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()


