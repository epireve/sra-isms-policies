# UM IT & ISMS Policy Document Gatherer

This project collects, converts, and catalogs IT and ISMS policy documents for the University of Malaya (UM). It supports both manual and automated (API-based) document discovery, saving all documents and their metadata for easy reference and analysis.

## Features
- Download and save PDF and web documents from a list of URLs
- Convert web pages to Markdown for easier reading
- Use the Serper API to automatically discover and download new policy documents
- Catalog all documents in a CSV file with metadata (URL, title, type, language, year, author, etc.)

## Project Structure
- `source.txt` — List of initial document URLs
- `download_documents.py` — Script to download and process documents from `source.txt`
- `serper_gather.py` — Script to use the Serper API to find and download new documents
- `documents_catalog.csv` — Catalog of all downloaded documents and their metadata
- `downloads/` — Folder where all documents are saved
- `.env` — Store your Serper API key as `SERPER_API_KEY=your_key_here`
- `.cursor/rules` — Project overview, goals, and requirements

## Setup
1. **Clone the repository and enter the project directory.**
2. **Create a virtual environment and install dependencies:**
   ```bash
   uv venv .venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```
3. **Add your Serper API key to a `.env` file:**
   ```env
   SERPER_API_KEY=your_key_here
   ```

## Usage
### 1. Download from `source.txt`
Run the following command to download and process all documents listed in `source.txt`:
```bash
python3 download_documents.py
```

### 2. Discover and download new documents using Serper API
Run the following command to search for and download new policy PDFs using the Serper API:
```bash
python3 serper_gather.py
```

All downloaded files will be saved in the `downloads/` folder, and the catalog will be updated in `documents_catalog.csv`.

## Notes
- Make sure your `.env` file is present and contains a valid Serper API key before running `serper_gather.py`.
- The scripts are beginner-friendly and well-commented for easy understanding and extension.

## License
MIT License 