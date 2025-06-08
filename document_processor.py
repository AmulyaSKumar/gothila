import PyPDF2
import docx
import logging
import re
from typing import Optional

class DocumentProcessor:
    """Handles text extraction from various document formats"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from document based on file type"""
        try:
            if file_type.lower() == 'pdf':
                return self._extract_from_pdf(file_path)
            elif file_type.lower() == 'docx':
                return self._extract_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            self.logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num + 1} ---\n"
                            text += page_text
                    except Exception as e:
                        self.logger.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                        
        except Exception as e:
            self.logger.error(f"Error reading PDF file: {str(e)}")
            raise
        
        return self._clean_text(text)
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = docx.Document(file_path)
            
            # Extract text from paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text += cell.text + " "
                    text += "\n"
                        
        except Exception as e:
            self.logger.error(f"Error reading DOCX file: {str(e)}")
            raise
        
        return self._clean_text(text)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Join lines back
        cleaned_text = '\n'.join(lines)
        
        return cleaned_text.strip()
    
    def get_document_stats(self, text: str) -> dict:
        """Get basic statistics about the document"""
        if not text:
            return {
                'word_count': 0,
                'character_count': 0,
                'paragraph_count': 0,
                'line_count': 0
            }
        
        words = text.split()
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        lines = [l for l in text.split('\n') if l.strip()]
        
        return {
            'word_count': len(words),
            'character_count': len(text),
            'paragraph_count': len(paragraphs),
            'line_count': len(lines)
        }
