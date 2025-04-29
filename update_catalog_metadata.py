import os
import pandas as pd
import re

# Helper function to guess language from filename or title
# This is a simple heuristic; for more accuracy, use a language detection library
# For now, we check for common language codes or keywords in the title/filename


def guess_language(row):
    title = row.get("title", "").lower()
    filename = str(row.get("local_path", "")).lower()
    # Check for Malay/English keywords
    if any(
        word in title or word in filename
        for word in ["malay", "bahasa", "dasar", "polisi", "penggunaan", "pembekal"]
    ):
        return "ms"  # Malay
    if any(
        word in title or word in filename
        for word in [
            "english",
            "policy",
            "security",
            "handbook",
            "management",
            "rules",
            "regulations",
        ]
    ):
        return "en"  # English
    # Fallback to existing value or blank
    return row.get("language", "") or ""


# Helper function to generate APA 7th edition reference
# This function creates a citation string based on the available metadata
# If author or year is missing, it uses 'No author' or 'n.d.'
def generate_apa_reference(row):
    author = row.get("author", "") or "No author"
    year = row.get("year", "") or "n.d."
    title = row.get("title", "") or "[No title]"
    url = row.get("url", "")
    doc_type = row.get("type", "")
    # APA 7th for web documents: Title. (Year). URL
    # APA 7th for PDFs (reports): Author. (Year). Title (PDF). URL
    if doc_type == "Web Document":
        # For web, author is often missing, so just use title and year
        return f"{title}. ({year}). {url}"
    else:
        # For PDF, use author, year, title, and url
        return f"{author}. ({year}). {title} (PDF). {url}"


# Main script to update the catalog
if __name__ == "__main__":
    # Load the CSV
    df = pd.read_csv("documents_catalog.csv")

    # Update language column using our guess_language function
    df["language"] = df.apply(guess_language, axis=1)

    # Ensure reference column exists and is up to date
    df["reference"] = df.apply(generate_apa_reference, axis=1)

    # Save the updated CSV
    df.to_csv("documents_catalog.csv", index=False)
    print("Catalog metadata updated: language and APA reference columns refreshed.")
