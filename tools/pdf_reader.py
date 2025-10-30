"""
tools/pdf_reader.py
Extract text and metadata from research papers (PDF)
"""

from pypdf import PdfReader
from typing import Dict, Any, Optional, List
import re
import os

class PDFReader:
    """
    PDF extraction tool for research papers
    
    Features:
    - Extract full text
    - Extract metadata (title, author, etc.)
    - Identify abstract
    - Extract sections
    - Handle multi-column layouts
    """

    def __init__(self):
        self.supported_extensions = ['.pdf']
        print("✅ PDF Reader initialized")
    

    def extract_text(self, pdf_path: str, max_pages: Optional[int] = None) -> str:
        """
        Extract all text from PDF
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to extract (None = all)
        
        Returns:
            Extracted text as string
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError(f"Not a PDF file: {pdf_path}")
        
        print(f"📖 Reading PDF: {pdf_path}")
        
        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            
            print(f"   Pages: {num_pages}")
            
            # Extract text from pages
            text_parts = []
            pages_to_read = min(num_pages, max_pages) if max_pages else num_pages
            
            for i in range(pages_to_read):
                page = reader.pages[i]
                page_text = page.extract_text()
                text_parts.append(page_text)
                
                if (i + 1) % 10 == 0:
                    print(f"   Processed {i + 1}/{pages_to_read} pages...")
            
            full_text = '\n\n'.join(text_parts)
            
            print(f"✅ Extracted {len(full_text)} characters from {pages_to_read} pages")
            
            return full_text
            
        except Exception as e:
            print(f"❌ PDF extraction error: {e}")
            raise
    

    def get_paper_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract metadata and basic info from PDF
        
        Returns:
        {
            'metadata': {...},
            'num_pages': int,
            'abstract': str,
            'sections': [...]
        }
        """
        print(f"📊 Extracting paper info from: {pdf_path}")
        
        try:
            reader = PdfReader(pdf_path)
            
            # Get metadata
            metadata = {}
            if reader.metadata:
                metadata = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', ''),
                    'creation_date': str(reader.metadata.get('/CreationDate', '')),
                }
            
            # Get number of pages
            num_pages = len(reader.pages)
            
            # Extract first few pages for abstract detection
            first_pages_text = ''
            for i in range(min(3, num_pages)):  # Check first 3 pages
                first_pages_text += reader.pages[i].extract_text() + '\n\n'
            
            # Try to extract abstract
            abstract = self._extract_abstract(first_pages_text)
            
            # Try to identify sections
            sections = self._extract_sections(first_pages_text)
            
            info = {
                'metadata': metadata,
                'num_pages': num_pages,
                'abstract': abstract,
                'sections': sections,
                'file_path': pdf_path,
                'file_size': os.path.getsize(pdf_path)
            }
            
            print(f"✅ Paper info extracted:")
            print(f"   Title: {metadata.get('title', 'Not found')[:50]}...")
            print(f"   Pages: {num_pages}")
            print(f"   Abstract: {'Found' if abstract else 'Not found'}")
            
            return info
            
        except Exception as e:
            print(f"❌ Error extracting paper info: {e}")
            return {
                'metadata': {},
                'num_pages': 0,
                'abstract': '',
                'sections': [],
                'error': str(e)
            }
    
    def _extract_abstract(self, text: str) -> str:
        """Try to extract abstract from paper text"""
        
        # Look for "Abstract" section
        # Common patterns:
        # - "Abstract\n"
        # - "ABSTRACT\n"
        # - "Abstract—"
        # - "Abstract:"
        
        patterns = [
            r'(?i)abstract[:\-—]\s*(.*?)(?=\n\s*\n|\n\s*1\.|\n\s*introduction|$)',
            r'(?i)abstract\s*\n\s*(.*?)(?=\n\s*\n|\n\s*1\.|\n\s*introduction|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                abstract = match.group(1).strip()
                
                # Clean up abstract
                abstract = re.sub(r'\s+', ' ', abstract)  # Remove extra whitespace
                abstract = abstract[:1000]  # Limit length
                
                if len(abstract) > 50:  # Must be substantial
                    return abstract
        
        return ''
    

    def _extract_sections(self, text: str) -> List[str]:
        """Try to identify paper sections"""
        
        # Common section patterns
        section_patterns = [
            r'(?i)^\s*\d+\.?\s+(introduction|background|related work|methodology|method|approach|experiments?|results?|evaluation|discussion|conclusion|references?)',
            r'(?i)^\s*(introduction|background|related work|methodology|method|approach|experiments?|results?|evaluation|discussion|conclusion)\s*\n'
        ]
        
        sections = []
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                section_name = match.group(1).strip()
                if section_name.lower() not in [s.lower() for s in sections]:
                    sections.append(section_name.title())
        
        return sections
    
    def extract_page_range(
        self,
        pdf_path: str,
        start_page: int,
        end_page: int
    ) -> str:
        """Extract text from specific page range"""
        
        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            
            # Validate range
            start_page = max(0, min(start_page, num_pages - 1))
            end_page = max(start_page, min(end_page, num_pages - 1))
            
            text_parts = []
            for i in range(start_page, end_page + 1):
                text_parts.append(reader.pages[i].extract_text())
            
            return '\n\n'.join(text_parts)
            
        except Exception as e:
            print(f"❌ Error extracting page range: {e}")
            return ''
    
    def search_text(self, pdf_path: str, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for text in PDF
        
        Returns list of matches with page numbers and context
        """
        print(f"🔍 Searching for '{search_term}' in {pdf_path}")
        
        try:
            reader = PdfReader(pdf_path)
            matches = []
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                
                # Find all occurrences
                pattern = re.compile(re.escape(search_term), re.IGNORECASE)
                
                for match in pattern.finditer(text):
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]
                    
                    matches.append({
                        'page': page_num + 1,
                        'context': context,
                        'position': match.start()
                    })
            
            print(f"✅ Found {len(matches)} matches")
            return matches
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
        
    
    def extract_references(self, pdf_path: str) -> List[str]:
        """Try to extract references/bibliography"""
        
        print(f"📚 Extracting references from {pdf_path}")
        
        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            
            # References usually in last few pages
            last_pages_text = ''
            start_page = max(0, num_pages - 5)
            
            for i in range(start_page, num_pages):
                last_pages_text += reader.pages[i].extract_text() + '\n\n'
            
            # Look for references section
            ref_pattern = r'(?i)(references?|bibliography)\s*\n\s*(.*?)(?=\n\s*appendix|\Z)'
            match = re.search(ref_pattern, last_pages_text, re.DOTALL)
            
            if match:
                ref_text = match.group(2)
                
                # Split into individual references
                # Common patterns: [1], (1), 1., numbered lines
                ref_lines = ref_text.split('\n')
                references = []
                current_ref = ''
                
                for line in ref_lines:
                    line = line.strip()
                    
                    # Check if new reference (starts with number)
                    if re.match(r'^\[?\d+\]?\.?\s+', line):
                        if current_ref:
                            references.append(current_ref.strip())
                        current_ref = line
                    else:
                        current_ref += ' ' + line
                
                if current_ref:
                    references.append(current_ref.strip())
                
                print(f"✅ Extracted {len(references)} references")
                return references[:50]  # Limit to first 50
            
            return []
            
        except Exception as e:
            print(f"❌ Error extracting references: {e}")
            return []
    
    def get_text_stats(self, pdf_path: str) -> Dict[str, Any]:
        """Get statistics about the PDF text"""
        
        try:
            text = self.extract_text(pdf_path)
            
            stats = {
                'total_characters': len(text),
                'total_words': len(text.split()),
                'total_lines': len(text.split('\n')),
                'estimated_tokens': len(text) // 4,  # Rough estimate
                'avg_word_length': sum(len(word) for word in text.split()) / max(len(text.split()), 1)
            }
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
        
    
    def validate_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Validate if PDF is readable and get basic info"""
        
        validation = {
            'valid': False,
            'exists': False,
            'is_pdf': False,
            'readable': False,
            'num_pages': 0,
            'has_text': False,
            'errors': []
        }
        
        # Check existence
        if not os.path.exists(pdf_path):
            validation['errors'].append('File does not exist')
            return validation
        
        validation['exists'] = True
        
        # Check extension
        if not pdf_path.lower().endswith('.pdf'):
            validation['errors'].append('Not a PDF file')
            return validation
        
        validation['is_pdf'] = True
        
        # Try to read
        try:
            reader = PdfReader(pdf_path)
            validation['readable'] = True
            validation['num_pages'] = len(reader.pages)
            
            # Check if has extractable text
            if validation['num_pages'] > 0:
                sample_text = reader.pages[0].extract_text()
                if len(sample_text.strip()) > 50:
                    validation['has_text'] = True
                    validation['valid'] = True
                else:
                    validation['errors'].append('PDF has no extractable text (may be scanned image)')
            else:
                validation['errors'].append('PDF has no pages')
                
        except Exception as e:
            validation['errors'].append(f'Read error: {str(e)}')
        
        return validation
    


# ==================== HELPER FUNCTIONS ====================

def clean_text(text: str) -> str:
    """Clean extracted PDF text"""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page numbers (common patterns)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    
    # Remove headers/footers (heuristic: short lines at top/bottom)
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip very short lines that might be headers/footers
        if len(line.strip()) > 20:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def extract_tables(text: str) -> List[str]:
    """Try to identify table-like structures in text"""
    
    tables = []
    lines = text.split('\n')
    
    # Look for lines with multiple tabs or aligned columns
    table_lines = []
    
    for line in lines:
        # Heuristic: if line has 3+ tabs or multiple sequences of spaces
        if line.count('\t') >= 3 or len(re.findall(r'\s{3,}', line)) >= 3:
            table_lines.append(line)
        elif table_lines:
            # End of table
            if len(table_lines) >= 3:
                tables.append('\n'.join(table_lines))
            table_lines = []
    
    return tables

# ==================== DEMO ====================

def demo_pdf_reader():
    """Demo the PDF Reader"""
    
    print("="*60)
    print("📄 PDF READER DEMO")
    print("="*60)
    print()
    
    reader = PDFReader()
    
    # Ask for PDF path
    print("Enter path to a PDF research paper to test:")
    pdf_path = input("Path: ").strip()
    
    if not pdf_path:
        print("⏭️  No path provided, exiting demo")
        return
    
    print()


 # Validate PDF
    print("🔍 Validating PDF...")
    validation = reader.validate_pdf(pdf_path)
    print(f"Valid: {validation['valid']}")
    
    if not validation['valid']:
        print(f"❌ Errors: {validation['errors']}")
        return
    
    print()


 # Get paper info
    print("📊 Extracting paper info...")
    info = reader.get_paper_info(pdf_path)
    
    print(f"\nMetadata:")
    for key, value in info['metadata'].items():
        if value:
            print(f"  {key}: {value}")
    
    print(f"\nPages: {info['num_pages']}")
    print(f"File size: {info['file_size']:,} bytes")
    
    if info['abstract']:
        print(f"\nAbstract (first 200 chars):")
        print(f"  {info['abstract'][:200]}...")
    
    if info['sections']:
        print(f"\nSections found: {', '.join(info['sections'])}")
    
    print()
    
    # Extract text
    print("📖 Extracting full text (first 5 pages)...")
    text = reader.extract_text(pdf_path, max_pages=5)
    
    print(f"\nExtracted text (first 500 chars):")
    print(f"  {text[:500]}...")
    
    # Get stats
    print("\n📈 Text statistics:")
    stats = reader.get_text_stats(pdf_path)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Search test
    print("\n🔍 Search test:")
    search_term = input("Enter term to search (or Enter to skip): ").strip()
    
    if search_term:
        matches = reader.search_text(pdf_path, search_term)
        print(f"\nFound {len(matches)} matches:")
        for i, match in enumerate(matches[:3], 1):
            print(f"\n  {i}. Page {match['page']}:")
            print(f"     ...{match['context']}...")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo_pdf_reader