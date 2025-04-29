import pandas as pd
import os
import shutil
from pathlib import Path

# Read the catalog
df = pd.read_csv("documents_catalog.csv")

# Create final_policy_documents directory if it doesn't exist
final_dir = Path("final_policy_documents")
final_dir.mkdir(exist_ok=True)

# Filter for markdown files (those with .md extension in local_path)
md_files = df[df["local_path"].str.endswith(".md", na=False)]

# Lists to track files
english_files = []
malay_files = []

# Process each markdown file
for _, row in md_files.iterrows():
    source_path = Path(row["local_path"])
    if not source_path.exists():
        print(f"Warning: Source file not found: {source_path}")
        continue

    # Check language
    if row["language"] in ["en", "en-US"]:
        english_files.append(str(source_path))
        # Copy to final directory
        dest_path = final_dir / source_path.name
        shutil.copy2(source_path, dest_path)
        print(f"Copied English file: {source_path.name}")
    elif row["language"] == "ms":
        malay_files.append(str(source_path))
        print(f"Identified Malay file for translation: {source_path.name}")

print("\nSummary:")
print(f"Total English files copied: {len(english_files)}")
print(f"Files requiring translation: {len(malay_files)}")

if malay_files:
    print("\nFiles needing translation:")
    for file in malay_files:
        print(f"- {file}")
