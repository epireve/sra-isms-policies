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

# Load the CSV
df = pd.read_csv("documents_catalog.csv")

# Add a new column for conversion status if not present
if "marker_conversion" not in df.columns:
    df["marker_conversion"] = ""

# Find all PDF files in the catalog
for idx, row in df.iterrows():
    if (
        row["type"] == "PDF Document"
        and isinstance(row["local_path"], str)
        and row["local_path"].endswith(".pdf")
    ):
        pdf_path = row["local_path"]
        try:
            # Build the marker command
            cmd = [
                "env",
                f"GOOGLE_API_KEY={GOOGLE_API_KEY}",
                MARKER_PATH,
                pdf_path,
                *MARKER_OPTIONS,
            ]
            # Run the marker CLI
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                df.at[idx, "marker_conversion"] = "success"
            else:
                df.at[idx, "marker_conversion"] = f"fail: {result.stderr.strip()}"
        except Exception as e:
            df.at[idx, "marker_conversion"] = f"fail: {str(e)}"

# Save the updated CSV
df.to_csv("documents_catalog.csv", index=False)
print("PDF conversion complete. Updated catalog saved.")
