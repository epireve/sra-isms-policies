import os
from pathlib import Path
from dotenv import load_dotenv
import time
from typing import Optional
import google.generativeai as genai
from google.api_core import retry

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# List available models
model_list = genai.list_models()
print("Available models:", [model.name for model in model_list])

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-pro-latest")


def translate_text(
    text: str, source_lang: str = "ms", target_lang: str = "en"
) -> Optional[str]:
    """
    Translate text using Gemini API.
    """
    try:
        prompt = f"""
        Please translate the following text from Bahasa Malaysia to English. 
        Maintain the original formatting, including any markdown syntax.
        Keep technical terms and proper nouns unchanged.
        
        Text to translate:
        {text}
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return None


def process_markdown_file(input_path: Path) -> Optional[str]:
    """Process and translate a markdown file."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split content into smaller chunks if needed (Gemini has a context limit)
        # For now, we'll translate the whole content at once
        translated_content = translate_text(content)

        if translated_content is None:
            raise Exception("Translation failed")

        return translated_content
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None


def save_malay_files_list(malay_files: list[str]):
    """Save the list of Malay files for translation."""
    with open("malay_files_to_translate.txt", "w", encoding="utf-8") as f:
        for file in malay_files:
            f.write(f"{file}\n")


def main():
    # Get list of Malay files from previous script
    final_dir = Path("final_policy_documents")
    final_dir.mkdir(exist_ok=True)

    # Process files identified by move_and_identify_translations.py
    try:
        with open("malay_files_to_translate.txt", "r") as f:
            malay_files = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(
            "No Malay files list found. Please run move_and_identify_translations.py first."
        )
        return

    for file_path in malay_files:
        input_path = Path(file_path)
        if not input_path.exists():
            print(f"Warning: File not found: {input_path}")
            continue

        print(f"Translating: {input_path.name}")

        try:
            # Translate content
            translated_content = process_markdown_file(input_path)

            if translated_content is None:
                print(f"Failed to translate {input_path.name}")
                continue

            # Save translated file
            output_path = final_dir / f"{input_path.stem}_en{input_path.suffix}"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(translated_content)

            print(f"Successfully translated and saved: {output_path.name}")

            # Add a small delay between translations
            time.sleep(2)

        except Exception as e:
            print(f"Error processing {input_path.name}: {str(e)}")


if __name__ == "__main__":
    main()
