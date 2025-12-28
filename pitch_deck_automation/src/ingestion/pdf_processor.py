import logging
from pypdf import PdfReader
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class PDFIngestor:
    @staticmethod
    def extract_text(file_path: str) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found at: {file_path}")
            
        if path.suffix.lower() != '.pdf':
            raise ValueError(f"File at {file_path} is not a PDF.")

        try:
            reader = PdfReader(path)
            text_content = []
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                else:
                    logger.warning(f"Could not extract text from page {page_num + 1}")
            
            full_text = "\n".join(text_content)
            logger.info(f"Successfully extracted {len(full_text)} characters from {path.name}")
            return full_text

        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {str(e)}")
            raise
