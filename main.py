import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def load_questions():
    path = "src/questions.txt"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [q.strip() for q in f.readlines() if q.strip()]

def answer(q):
    model = genai.GenerativeModel("gemini-2.0-flash")
    r = model.generate_content(q)
    return r.text

def main():
    questions = load_questions()
    if not questions:
        print("No questions found.")
        return

    os.makedirs("output", exist_ok=True)
    with open("output/output.txt", "w", encoding="utf-8") as f:
        for q in questions:
            print("Q:", q)
            try:
                a = answer(q)
                f.write(f"Q: {q}\nA: {a}\n\n")
            except Exception as e:
                f.write(f"Q: {q}\nError: {e}\n\n")

if __name__ == "__main__":
    main()
