# py_wget.py
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def recursive_download(start_url, output_dir, allowed_domain, wait_time=1):
    """
    指定されたURLから再帰的にHTMLファイルをダウンロードする関数。
    wget --recursive --no-parent --accept=html と似た動作をします。
    """
    urls_to_visit = {start_url}
    visited_urls = set()

    # 出力ディレクトリがなければ作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 訪問すべきURLがなくなるまでループ
    while urls_to_visit:
        current_url = urls_to_visit.pop()

        if current_url in visited_urls:
            continue

        print(f"訪問中: {current_url}")
        visited_urls.add(current_url)

        try:
            # ページを取得
            response = requests.get(current_url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status() # エラーがあれば例外を発生
        except requests.exceptions.RequestException as e:
            print(f"  エラー: スキップします ({e})")
            continue

        # HTMLを解析
        soup = BeautifulSoup(response.content, 'lxml')

        # --- ファイルの保存ロジック ---
        # URLのパス部分からローカルのファイルパスを構築
        parsed_url = urlparse(current_url)
        # 先頭のスラッシュを削除
        local_path = parsed_url.path.lstrip('/')
        # ファイル名がなければ index.html とする
        if local_path.endswith('/'):
            local_path += "index.html"
        elif not os.path.splitext(local_path)[1]: # 拡張子がない場合
             local_path += "/index.html"
        
        file_path = os.path.join(output_dir, local_path)
        
        # 保存先のディレクトリを作成
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # ファイルを保存
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"  保存先: {file_path}")

        # --- 新しいリンクの探索ロジック ---
        # ページ内のすべての<a>タグ（リンク）を探す
        for link in soup.find_all('a', href=True):
            href = link['href']
            # 相対URLを絶対URLに変換 (例: "../page.html" -> "https://.../page.html")
            new_url = urljoin(current_url, href)
            
            # URLから#以降のアンカーを削除 (例: "...page.html#section1" -> "...page.html")
            new_url = new_url.split('#')[0]

            # --- ルールに合致するかチェック ---
            # 1. 許可されたドメインか？ (--domains)
            # 2. スタートURLのパス配下か？ (--no-parent)
            # 3. まだ訪問していないか？
            # 4. HTMLファイルか？ (拡張子なし or .html) (--accept=html)
            if (urlparse(new_url).netloc == allowed_domain and
                new_url.startswith(start_url) and
                new_url not in visited_urls and
                (not os.path.splitext(urlparse(new_url).path)[1] or 
                 os.path.splitext(urlparse(new_url).path)[1] == '.html')):
                
                urls_to_visit.add(new_url)

        # サーバーに負荷をかけないように待機 (--wait)
        time.sleep(wait_time)

    print("\nダウンロードが完了しました。")


if __name__ == "__main__":
    # --- ここでダウンロードしたいサイトの設定を切り替える ---
    # 【設定1】Google Apps Scriptのドキュメントをダウンロードする場合

    print("--- Google Apps Script ドキュメントのダウンロードを開始します ---")
    recursive_download(
        start_url="https://developers.google.com/apps-script/reference/",
        output_dir="gas_docs_html",
        allowed_domain="developers.google.com"
    )

    print("\n" + "="*50 + "\n")

    # 【設定2】Gemini APIのドキュメントをダウンロードする場合
    print("--- Gemini API ドキュメントのダウンロードを開始します ---")
    recursive_download(
        start_url="https://ai.google.dev/gemini-api/docs/",
        output_dir="gemini_api_docs_html",
        allowed_domain="ai.google.dev"
    )