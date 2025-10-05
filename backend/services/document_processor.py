import logging
from typing import Optional
from PIL import Image
import pytesseract
import PyPDF2
import pdfplumber
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Handles document text extraction for various file types
    Supports: PDF, JPG, PNG
    """

    def __init__(self):
        self.supported_formats = ['pdf', 'jpg', 'jpeg', 'png', 'txt']

    async def extract_text(self, file_path: str) -> str:
        file_extension = file_path.split('.')[-1].lower()
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")

        if file_extension == 'pdf':
            return await self._extract_from_pdf(file_path)
        elif file_extension == 'txt':
            return await self._extract_from_txt(file_path)
        else:
            return await self._extract_from_image(file_path)

    async def _extract_from_pdf(self, file_path: str) -> str:
        text = ""

        try:
            # Try pdfplumber first (better for structured data like lab reports)
            def _pdfplumber_read(path):
                out = ""
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            out += page_text + "\n"
                return out

            text = await run_in_threadpool(_pdfplumber_read, file_path)

            # If no text extracted, try PyPDF2
            if not text.strip():
                logger.info("pdfplumber extraction empty, trying PyPDF2")

                def _pypdf2_read(path):
                    out = ""
                    with open(path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            try:
                                ptext = page.extract_text()
                                if ptext:
                                    out += ptext + "\n"
                            except Exception:
                                continue
                    return out

                text = await run_in_threadpool(_pypdf2_read, file_path)

            # If still no text, PDF might be scanned - use OCR
            if not text.strip():
                logger.info("PDF appears to be scanned or contains images, using OCR")
                text = await self._ocr_pdf(file_path)

            return self.clean_text(text)

        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise

    async def _extract_from_image(self, file_path: str) -> str:
        try:
            def _image_ocr(path):
                img = Image.open(path)
                img = img.convert('L')
                return pytesseract.image_to_string(img)

            text = await run_in_threadpool(_image_ocr, file_path)
            return self.clean_text(text)

        except Exception as e:
            logger.error(f"Image OCR error: {e}")
            raise

    async def _ocr_pdf(self, file_path: str) -> str:
        try:
            import pdf2image

            def _pdf2img(path):
                return pdf2image.convert_from_path(path)

            images = await run_in_threadpool(_pdf2img, file_path)

            out = ""
            for i, image in enumerate(images):
                logger.info(f"OCR processing page {i+1}/{len(images)}")
                out += pytesseract.image_to_string(image) + "\n"

            return self.clean_text(out)

        except Exception as e:
            logger.error(f"PDF OCR error: {e}")
            raise

    async def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from a text file"""
        try:
            def _read_txt(path):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            
            text = await run_in_threadpool(_read_txt, file_path)
            return self.clean_text(text)
        except Exception as e:
            logger.error(f"Text file read error: {e}")
            raise

    def clean_text(self, text: str) -> str:
        # Remove multiple spaces
        cleaned = ' '.join(text.split())
        # Preserve paragraph breaks by splitting on double-newline and rejoining
        lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
        return '\n'.join(lines)
