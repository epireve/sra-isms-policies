import os
import json
import requests
import pandas as pd
from urllib.parse import urlparse
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY") or os.getenv("X-API-KEY")


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
            return filename, title, year, author, info
        except Exception as e:
            return filename, os.path.basename(filename), "", "", {}
    except Exception as e:
        print(f"Failed to download PDF: {url}\nError: {e}")
        return "", "", "", "", {}


# Helper function to generate APA 7th edition reference
# This function creates a citation string based on the available metadata
# If author or year is missing, it uses 'No author' or 'n.d.'
def generate_apa_reference(row):
    author = row.get("author", "") or "No author"
    year = row.get("year", "") or "n.d."
    title = row.get("title", "") or "[No title]"
    url = row.get("url", "")
    doc_type = row.get("type", "")
    # APA 7th for web documents: Title. (Year). Site Name. URL
    # APA 7th for PDFs (reports): Author. (Year). Title (PDF). URL
    if doc_type == "Web Document":
        # For web, author is often missing, so just use title and year
        return f"{title}. ({year}). {url}"
    else:
        # For PDF, use author, year, title, and url
        return f"{author}. ({year}). {title} (PDF). {url}"


def main():
    save_dir = "downloads"
    os.makedirs(save_dir, exist_ok=True)
    # Load existing CSV if exists
    if os.path.exists("documents_catalog.csv"):
        df = pd.read_csv("documents_catalog.csv")
    else:
        df = pd.DataFrame()
    # Prepare Serper API request
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = json.dumps({"q": "site:https://it.um.edu.my/doc/Policy", "gl": "my"})
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code != 200:
        print("Serper API error:", response.text)
        return
    results = response.json()
    # Extract PDF links from results
    pdf_links = set()
    for section in [
        "organic",
        "news",
        "videos",
        "images",
        "shopping",
        "local",
        "answerBox",
        "peopleAlsoAsk",
    ]:
        items = results.get(section, [])
        if isinstance(items, dict):
            items = [items]
        for item in items:
            link = item.get("link")
            if link and link.lower().endswith(".pdf"):
                pdf_links.add(link)
    # Download and catalog new PDFs
    new_rows = []
    for url in pdf_links:
        if not df.empty and url in df["url"].values:
            continue  # Skip if already cataloged
        filename, title, year, author, meta = download_pdf(url, save_dir)
        row = {
            "url": url,
            "title": title,
            "type": "PDF Document",
            "language": "",
            "year": year,
            "author": author,
            "local_path": filename,
            "extra_metadata": str(meta),
        }
        # Add APA reference column
        row["reference"] = generate_apa_reference(row)
        new_rows.append(row)
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.to_csv("documents_catalog.csv", index=False)
        print(f"Added {len(new_rows)} new PDFs to catalog.")
    else:
        print("No new PDFs found or added.")


if __name__ == "__main__":
    main()
