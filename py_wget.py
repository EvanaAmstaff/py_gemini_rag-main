# py_wget_playwright.py
import os
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def recursive_download(start_url, output_dir, allowed_domain, wait_time=1):
    """
    Playwright を使って JS レンダリング済み HTML を再帰ダウンロード。
    wget --recursive の HTML 版に相当。
    """

    urls_to_visit = {start_url}
    visited_urls = set()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        while urls_to_visit:
            current_url = urls_to_visit.pop()

            if current_url in visited_urls:
                continue

            print(f"訪問中: {current_url}")
            visited_urls.add(current_url)

            try:
                page.goto(current_url, timeout=30000)  # 30秒
                page.wait_for_load_state("networkidle")
                html = page.content()
            except Exception as e:
                print(f"  エラー: スキップします ({e})")
                continue

            soup = BeautifulSoup(html, "lxml")

            parsed = urlparse(current_url)
            local_path = parsed.path.lstrip("/")

            if local_path.endswith("/"):
                local_path += "index.html"
            elif not os.path.splitext(local_path)[1]:
                local_path += "/index.html"

            file_path = os.path.join(output_dir, local_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  保存先: {file_path}")

            # --- 再帰リンク探索 ---
            for link in soup.find_all("a", href=True):
                href = link["href"]

                new_url = urljoin(current_url, href)
                new_url = new_url.split("#")[0]

                parsed_new = urlparse(new_url)
                ext = os.path.splitext(parsed_new.path)[1]

                if (
                    parsed_new.netloc == allowed_domain and
                    new_url.startswith(start_url) and
                    new_url not in visited_urls and
                    (ext == "" or ext == ".html")
                ):
                    urls_to_visit.add(new_url)

            time.sleep(wait_time)

        browser.close()

    print("\nダウンロード完了！")


if __name__ == "__main__":

    print("\n--- Google Apps Script ドキュメント ---")
    recursive_download(
        start_url="https://developers.google.com/apps-script/reference/",
        output_dir="gas_docs_html",
        allowed_domain="developers.google.com"
    )

    print("\n" + "=" * 60 + "\n")

    print("--- Gemini API ドキュメント ---")
    recursive_download(
        start_url="https://ai.google.dev/gemini-api/docs/",
        output_dir="gemini_api_docs_html",
        allowed_domain="ai.google.dev"
    )
