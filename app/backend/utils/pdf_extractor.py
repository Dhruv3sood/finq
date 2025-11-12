import PyPDF2
import io
from typing import Optional

class PDFExtractor:
    """Extract text content from PDF files"""
    
    @staticmethod
    def extract_text(pdf_file) -> str:
        """
        Extract text from a PDF file
        
        Args:
            pdf_file: File-like object (Flask file upload or BytesIO)
            
        Returns:
            Extracted text content as string
        """
        try:
            # Read the PDF file
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_content.append(text)
            
            # Join all pages with newlines
            full_text = '\n\n'.join(text_content)
            
            if not full_text.strip():
                raise ValueError("No text content found in PDF. The PDF might be image-based or encrypted.")
            
            return full_text
        
        except PyPDF2.errors.PdfReadError as e:
            raise ValueError(f"Error reading PDF file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def is_pdf_file(filename: str) -> bool:
        """Check if file is a PDF based on extension"""
        return filename.lower().endswith('.pdf')

