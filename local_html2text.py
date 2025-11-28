import os
import glob
from bs4 import BeautifulSoup

def convert_html_folder(html_folder, txt_folder, merged_filename):
    """HTML フォルダ → TXT フォルダ → 結合ファイル を生成する関数"""

    if not os.path.isdir(html_folder):
        print(f"⚠ HTML フォルダが見つかりません: {html_folder}")
        return False

    os.makedirs(txt_folder, exist_ok=True)

    html_files = glob.glob(os.path.join(html_folder, "**/*.html"), recursive=True)
    if not html_files:
        print(f"⚠ HTML ファイルがありません: {html_folder}")
        return False

    print(f"📁 HTML → TXT 変換開始: {html_folder} → {txt_folder}")
    merged_path = os.path.join(txt_folder, merged_filename)

    with open(merged_path, "w", encoding="utf-8") as merged_out:

        for html_file in html_files:
            try:
                with open(html_file, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    text = soup.get_text(separator="\n")

                # 出力 TXT ファイル名
                base = os.path.splitext(os.path.basename(html_file))[0]
                txt_path = os.path.join(txt_folder, base + ".txt")

                with open(txt_path, "w", encoding="utf-8") as out:
                    out.write(text)

                merged_out.write(f"\n\n===== FILE: {html_file} =====\n\n")
                merged_out.write(text)

                print(f"✔ 変換: {html_file}")

            except Exception as e:
                print(f"❌ エラー ({html_file}): {e}")

    print(f"🎉 完了: 結合ファイル作成 → {merged_path}")
    return True


def main():
    print("\n============================")
    print("📄 HTML → TXT 変換スクリプト開始")
    print("============================\n")

    # GAS
    convert_html_folder(
        html_folder="gas_docs_html",
        txt_folder="gas_docs_txt",
        merged_filename="gas_all.txt"
    )

    # Gemini API
    convert_html_folder(
        html_folder="gemini_api_docs_html",
        txt_folder="gemini_api_docs_txt",
        merged_filename="gemini_all.txt"
    )

    print("\n🚀 全処理完了\n")


if __name__ == "__main__":
    main()
