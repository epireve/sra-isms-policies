import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from PyPDF2 import PdfReader


# Helper function to determine file type
def get_file_type(url):
    if url.lower().endswith(".pdf"):
        return "pdf"
    return "web"


# Helper function to download PDF and extract metadata
def download_pdf(url, save_dir):
    try:
        response = requests.get(url)
        response.raise_for_status()
        filename = os.path.join(save_dir, url.split("/")[-1])
        with open(filename, "wb") as f:
            f.write(response.content)
        # Try to extract metadata
        try:
            reader = PdfReader(filename)
            info = reader.metadata
            title = info.title if info.title else os.path.basename(filename)
            author = info.author if info.author else ""
            year = (
                info.get("/CreationDate", "")[2:6] if info.get("/CreationDate") else ""
            )
            # Add more metadata fields as needed
            return filename, title, year, author, info
        except Exception as e:
            return filename, os.path.basename(filename), "", "", {}
    except Exception as e:
        print(f"Failed to download PDF: {url}\nError: {e}")
        return "", "", "", "", {}


# Helper function to download web page, convert to markdown, and extract metadata
def download_web(url, save_dir):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract title
        title = soup.title.string.strip() if soup.title else os.path.basename(url)
        # Try to guess language
        lang = soup.html.get("lang", "") if soup.html else ""
        # Convert to markdown
        markdown = md(response.text)
        # Save markdown
        safe_title = re.sub(r"\W+", "_", title)[:50]  # Limit filename length
        filename = os.path.join(save_dir, safe_title + ".md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(markdown)
        # Try to extract year from text (very basic)
        year_match = re.search(r"(20\d{2}|19\d{2})", response.text)
        year = year_match.group(0) if year_match else ""
        return filename, title, lang, year, {}
    except Exception as e:
        print(f"Failed to download web page: {url}\nError: {e}")
        return "", "", "", "", {}


# Main script
def main():
    save_dir = "downloads"
    os.makedirs(save_dir, exist_ok=True)
    csv_rows = []
    with open("source.txt") as f:
        urls = [line.strip() for line in f if line.strip()]
    for url in urls:
        doc_type = get_file_type(url)
        if doc_type == "pdf":
            filename, title, year, author, meta = download_pdf(url, save_dir)
            row = {
                "url": url,
                "title": title,
                "type": "PDF Document",
                "language": "",  # PDFs rarely have language metadata
                "year": year,
                "author": author,
                "local_path": filename,
                "extra_metadata": str(meta),
            }
        else:
            filename, title, lang, year, meta = download_web(url, save_dir)
            row = {
                "url": url,
                "title": title,
                "type": "Web Document",
                "language": lang,
                "year": year,
                "author": "",
                "local_path": filename,
                "extra_metadata": str(meta),
            }
        csv_rows.append(row)
    # Save CSV
    df = pd.DataFrame(csv_rows)
    df.to_csv("documents_catalog.csv", index=False)
    print("Download and catalog complete!")


if __name__ == "__main__":
    main()
