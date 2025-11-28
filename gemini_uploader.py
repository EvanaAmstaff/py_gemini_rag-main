import google.generativeai as genai
import os
import time
from pathlib import Path

API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# --- ファイルアップロード ---
def upload_files(dir_path="data"):
    uploaded_files = []
    for file in Path(dir_path).glob("*"):
        print(f"Uploading: {file}")
        uploaded = genai.upload_file(path=str(file))
        uploaded_files.append(uploaded)
    return uploaded_files

# --- 質問処理（429 の自動リトライ対応）---
def ask_gemini(question, file_refs):
    model = genai.GenerativeModel("gemini-2.0-flash")

    while True:
        try:
            result = model.generate_content(
                [question] + file_refs,
                safety_settings={"HARASSMENT": "BLOCK_NONE"},
            )
            return result.text

        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                print("Quota error. Waiting 40s…")
                time.sleep(40)
                continue
            else:
                return f"Error: {e}"

if __name__ == "__main__":
    files = upload_files("data")
    file_refs = [f"file:{f.uri}" for f in files]

    questions = Path("questions.txt").read_text().splitlines()
    output = []

    for q in questions:
        if not q.strip():
            continue
        print(f"Q: {q}")
        a = ask_gemini(q, file_refs)
        output.append(f"## Q: {q}\n\n{a}\n\n---\n")

    Path("gemini_output.md").write_text("\n".join(output), encoding="utf-8")
    print("Done: gemini_output.md")
