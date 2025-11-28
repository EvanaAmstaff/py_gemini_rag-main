# playwright_wget.py
import os
import time
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def save_html(content, output_dir, url):
    parsed_url = urlparse(url)
    local_path = parsed_url.path.lstrip('/')

    if local_path.endswith('/'):
        local_path += "index.html"
    elif not os.path.splitext(local_path)[1]:
        local_path += "/index.html"

    file_path = os.path.join(output_dir, local_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  保存: {file_path}")


def recursive_download_with_playwright(start_url, output_dir, allowed_domain, wait_time=1):
    urls_to_visit = {start_url}
    visited_urls = set()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        while urls_to_visit:
            url = urls_to_visit.pop()
            if url in visited_urls:
                continue

            visited_urls.add(url)
            print(f"訪問: {url}")

            try:
                page.goto(url, timeout=60000)
                time.sleep(1)  # JSロード待ち
            except Exception as e:
                print(f"  ⚠ ページ取得失敗: {e}")
                continue

            html = page.content()
            save_html(html, output_dir, url)

            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link["href"]
                new_url = urljoin(url, href).split("#")[0]

                parsed = urlparse(new_url)

                if parsed.netloc != allowed_domain:
                    continue
                if not new_url.startswith(start_url):
                    continue
                if new_url in visited_urls:
                    continue

                ext = os.path.splitext(parsed.path)[1]
                if ext not in ["", ".html"]:
                    continue

                urls_to_visit.add(new_url)

            time.sleep(wait_time)

        browser.close()

    print("\n📥 ダウンロード完了\n")


if __name__ == "__main__":
    print("\n--- Google Apps Script ドキュメント ---")
    recursive_download_with_playwright(
        start_url="https://developers.google.com/apps-script/reference/",
        output_dir="gas_docs_html",
        allowed_domain="developers.google.com"
    )

    print("\n--- Gemini API ドキュメント ---")
    recursive_download_with_playwright(
        start_url="https://ai.google.dev/gemini-api/docs/",
        output_dir="gemini_api_docs_html",
        allowed_domain="ai.google.dev"
    )
