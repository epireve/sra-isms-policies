import os
import subprocess
import pandas as pd

# Configuration
INPUT_DIR = "downloads"
OUTPUT_DIR = "policy_docs"
MARKER_PATH = (
    "/Users/invoture/dev.local/academic-agent/.venv/bin/marker"  # Update if needed
)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
WORKERS = "4"
MARKER_OPTIONS = [
    "--output_format",
    "markdown",
    "--output_dir",
    OUTPUT_DIR,
    "--use_llm",
    "--disable_image_extraction",
    "--workers",
    WORKERS,
]

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Run marker on the whole downloads/ folder
cmd = [
    "env",
    f"GOOGLE_API_KEY={GOOGLE_API_KEY}",
    MARKER_PATH,
    INPUT_DIR,
    *MARKER_OPTIONS,
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("Marker batch conversion completed.")
else:
    print("Marker batch conversion failed:", result.stderr)

# Load the CSV
df = pd.read_csv("documents_catalog.csv")

# Add a new column for conversion status if not present
if "marker_conversion" not in df.columns:
    df["marker_conversion"] = ""

# Check for each PDF if the corresponding Markdown file exists
for idx, row in df.iterrows():
    if (
        row["type"] == "PDF Document"
        and isinstance(row["local_path"], str)
        and row["local_path"].endswith(".pdf")
    ):
        pdf_filename = os.path.splitext(os.path.basename(row["local_path"]))[0]
        # Marker outputs .md files with the same base name
        md_path = os.path.join(OUTPUT_DIR, pdf_filename + ".md")
        if os.path.exists(md_path):
            df.at[idx, "marker_conversion"] = "success"
        else:
            df.at[idx, "marker_conversion"] = "fail: markdown not found"

# Save the updated CSV
df.to_csv("documents_catalog.csv", index=False)
print("PDF conversion status updated in catalog.")
