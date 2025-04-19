from pathlib import Path
from typing import List

import PyPDF2


def search_pdfs(directory: str, keywords: List[str]) -> List[str]:
    pdf_dir = Path(directory)
    matching_files = []

    for pdf_file in pdf_dir.glob("*.pdf"):
        try:
            with open(pdf_file, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text().lower()

                if any(keyword.lower() in text for keyword in keywords):
                    matching_files.append(pdf_file.name)
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")

    return matching_files


if __name__ == "__main__":
    directory = "drive-download-20250413T062715Z-001"
    keywords = ["facebook", "instagram"]

    matches = search_pdfs(directory, keywords)

    if matches:
        print("\nPDFs containing the keywords:")
        for match in matches:
            print(f"- {match}")
    else:
        print("\nNo PDFs found containing the specified keywords.")
