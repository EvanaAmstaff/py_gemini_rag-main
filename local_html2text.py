# local_html2text.py (【最終修正版】)
import os
import sys
from bs4 import BeautifulSoup
import glob

def convert_html_to_text(html_dir, output_dir):
    """
    指定されたディレクトリ内のHTMLファイルをテキストに変換して保存する。
    ディレクトリ構造を反映したユニークなファイル名を生成する。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    search_path = os.path.join(html_dir, '**', '*.html')
    html_files = glob.glob(search_path, recursive=True)

    if not html_files:
        print(f"HTMLファイルが見つかりませんでした。ディレクトリ '{html_dir}' を確認してください。")
        return

    print(f"{len(html_files)} 個のHTMLファイルを処理します...")

    for html_path in html_files:
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'lxml')

            content_div = soup.find('div', attrs={'class': 'devsite-article-body'})
            
            if content_div:
                # ▼▼▼【ここからが修正箇所】▼▼▼
                
                # 1. 入力ディレクトリからの相対パスを取得
                # 例: 'reference/spreadsheet/index.html'
                relative_path = os.path.relpath(html_path, html_dir)

                # 2. 拡張子を取り除き、ディレクトリ区切り文字をハイフンに置換
                # 例: 'reference-spreadsheet-index'
                base_name_without_ext = os.path.splitext(relative_path)[0]
                unique_base_name = base_name_without_ext.replace(os.sep, '-')

                # 3. 新しいファイル名を作成
                # 例: 'reference-spreadsheet-index.txt'
                output_filename = f"{unique_base_name}.txt"
                output_path = os.path.join(output_dir, output_filename)
                
                # ▲▲▲【ここまでが修正箇所】▲▲▲
                
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(f"Source Path: {html_path}\n\n")
                    out_f.write(content_div.get_text(separator='\n', strip=True))
                
                print(f"変換完了: {output_path}")

        except Exception as e:
            print(f"エラーが発生しました ({html_path}): {e}")

# --- GitHub Actions と ローカル実行の両方に対応 ---
if __name__ == "__main__":
    if len(sys.argv) == 3:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
        print(f"--- Processing files from '{input_dir}' to '{output_dir}' (from command line) ---")
        convert_html_to_text(input_dir, output_dir)
    else:
        print("--- Running with default settings for local testing ---")
        
        # --- ローカルでテスト実行したい場合の設定 ---
        # 既存のテキストフォルダを一度削除すると確実です
        if os.path.exists('gas_docs_txt'):
             import shutil
             shutil.rmtree('gas_docs_txt')
        if os.path.exists('gemini_api_docs_txt'):
             import shutil
             shutil.rmtree('gemini_api_docs_txt')

        # GAS
        convert_html_to_text('gas_docs_html', 'gas_docs_txt')
        # Gemini API
        convert_html_to_text('gemini_api_docs_html', 'gemini_api_docs_txt')