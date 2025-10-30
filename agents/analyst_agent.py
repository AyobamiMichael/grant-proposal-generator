"""
agents/analyst_agent.py
Extract and analyze research paper content
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo_phase1 import BaseAgent, Message, MessageType
from typing import Dict, Any
import json


class AnalystAgent(BaseAgent):
    """
    Analyst Agent - Paper Analysis & Information Extraction
    
    Role: Extract structured information from research papers
    Personality: Precise, detail-oriented, technical
    
    Capabilities:
    - Extract paper metadata (title, authors, year)
    - Identify key contributions
    - Analyze methodology
    - Assess novelty
    - Identify gaps and unclear sections
    """

    def __init__(self, message_queue, llm, pdf_reader):
        super().__init__(
            name="analyst",
            role="Paper Analysis & Information Extraction",
            message_queue=message_queue
        )
        self.llm = llm
        self.pdf_reader = pdf_reader
    

     
    def process(self, message: Message) -> Dict[str, Any]:
        """
        Process analysis request
        
        Expected message content:
        {
            'action': 'analyze',
            'paper_path': 'path/to/paper.pdf'
        }
        
        Returns:
        {
            'title': '...',
            'authors': [...],
            'key_contributions': [...],
            'methodology': {...},
            'results': {...},
            'novelty_assessment': {...},
            'gaps_identified': [...]
        }
        """
        action = message.content.get('action')
        
        if action != 'analyze':
            return {'error': f'Unknown action: {action}'}
        
        paper_path = message.content.get('paper_path')
        
        if not paper_path:
            return {'error': 'No paper_path provided'}
        
        print(f"📄 Analyst: Processing paper: {paper_path}")
        
        try:
            # Extract text from PDF
            paper_info = self.pdf_reader.get_paper_info(paper_path)
            full_text = self.pdf_reader.extract_text(paper_path)
            
            print(f"✅ Analyst: Extracted {len(full_text)} characters")
            
            # Analyze paper
            analysis = self._analyze_paper(
                full_text=full_text[:10000],  # First 10K chars
                abstract=paper_info.get('abstract', ''),
                metadata=paper_info.get('metadata', {})
            )
            
            print(f"✅ Analyst: Analysis complete")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Analyst error: {e}")
            return {'error': str(e)}
        
    def _analyze_paper(
        self,
        full_text: str,
        abstract: str,
        metadata: Dict
    ) -> Dict[str, Any]:
        """Use LLM to extract structured information"""
        
        print("🧠 Analyst: Calling LLM for analysis...")
        
        # Build analysis prompt
        prompt = f"""Analyze this research paper and extract key information.

Paper Metadata:
- Title: {metadata.get('title', 'Not found')}
- Author: {metadata.get('author', 'Not found')}
- Pages: {metadata.get('num_pages', 'Unknown')}

Abstract:
{abstract if abstract else 'Abstract not extracted'}

Paper Text (first part):
{full_text}

Extract the following information:
1. **Title**: The paper's title (if not in metadata, extract from text)
2. **Authors**: List of author names
3. **Year**: Publication year if mentioned
4. **Venue**: Conference or journal name if mentioned
5. **Key Contributions**: 3-5 main contributions of this paper
6. **Methodology**: Brief description of the approach/method used
7. **Datasets**: What datasets were used (if any)
8. **Evaluation Metrics**: Metrics used to evaluate (if mentioned)
9. **Main Results**: Key findings or performance improvements
10. **Limitations**: Any limitations mentioned by authors
11. **Novelty Score**: Rate the novelty from 0-10 with brief reasoning
12. **Gaps**: Any unclear sections or missing information

Be precise and extract only information clearly stated in the paper."""
        

        # Define expected schema
        schema = {
            "title": "string",
            "authors": ["string"],
            "year": "number or null",
            "venue": "string or null",
            "key_contributions": ["string"],
            "methodology": {
                "approach": "string",
                "datasets": ["string"],
                "evaluation_metrics": ["string"]
            },
            "main_results": {
                "summary": "string",
                "performance_improvements": ["string"]
            },
            "limitations": ["string"],
            "novelty_assessment": {
                "score": "number (0-10)",
                "reasoning": "string"
            },
            "gaps_identified": ["string"]
        }
        
          # Call LLM with structured output
        try:
            analysis = self.llm.generate_structured(
                prompt=prompt,
                schema=schema,
                max_tokens=2000,
                temperature=0.3  # Lower for more precise extraction
            )
            
            print(f"✅ Analyst: LLM analysis successful")
            
            # Add metadata
            analysis['extraction_metadata'] = {
                'source': metadata.get('title', 'Unknown'),
                'pages': metadata.get('num_pages', 0),
                'text_length': len(full_text),
                'abstract_available': bool(abstract)
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Analyst LLM error: {e}")
            
            # Return fallback analysis
            return {
                'title': metadata.get('title', 'Unknown'),
                'authors': [metadata.get('author', 'Unknown')],
                'year': None,
                'venue': None,
                'key_contributions': ['Could not extract - LLM error'],
                'methodology': {
                    'approach': 'Could not extract',
                    'datasets': [],
                    'evaluation_metrics': []
                },
                'main_results': {
                    'summary': 'Could not extract',
                    'performance_improvements': []
                },
                'limitations': [],
                'novelty_assessment': {
                    'score': 0,
                    'reasoning': f'Analysis failed: {str(e)}'
                },
                'gaps_identified': [f'LLM analysis error: {str(e)}'],
                'error': str(e)
            }
    
    def quick_summary(self, paper_path: str) -> str:
        """Generate a quick one-paragraph summary"""
        
        print(f"📝 Analyst: Generating quick summary for {paper_path}")
        
        try:
            paper_info = self.pdf_reader.get_paper_info(paper_path)
            text_sample = self.pdf_reader.extract_text(paper_path)[:5000]
            
            prompt = f"""Provide a concise one-paragraph summary of this research paper.

Title: {paper_info.get('metadata', {}).get('title', 'Unknown')}

Text:
{text_sample}


Summary (1 paragraph, 3-5 sentences):"""
            
            summary = self.llm.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.5
            )
            
            return summary.strip()
            
        except Exception as e:
            return f"Could not generate summary: {str(e)}"
    
    def identify_research_gaps(self, analysis: Dict[str, Any]) -> list:
        """Identify potential research gaps based on analysis"""
        
        print("🔍 Analyst: Identifying research gaps...")
        
        prompt = f"""Based on this paper analysis, identify 3-5 potential research gaps or future directions:

Key Contributions:
{json.dumps(analysis.get('key_contributions', []), indent=2)}

Methodology:
{json.dumps(analysis.get('methodology', {}), indent=2)}

Limitations:
{json.dumps(analysis.get('limitations', []), indent=2)}

Identify:
1. What questions remain unanswered?
2. What extensions could be explored?
3. What weaknesses could be addressed?
4. What new applications could be investigated?

Provide 3-5 concrete research gaps."""
        
        try:
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            # Parse into list
            gaps = [line.strip() for line in response.split('\n') if line.strip()]
            return gaps
            
        except Exception as e:
            print(f"❌ Gap identification error: {e}")
            return ["Could not identify gaps due to error"]
        

# ==================== DEMO ====================

def demo_analyst():
    """Demo the Analyst Agent"""
    
    print("="*60)
    print("📊 ANALYST AGENT DEMO")
    print("="*60)
    print()
    
    # Initialize dependencies
    from llm_wrapper import LLMWrapper
    from pdf_reader import PDFReader
    from demo_phase1 import MessageQueue
    
    llm = LLMWrapper(model='fast')
    pdf_reader = PDFReader()
    queue = MessageQueue()
    
      # Create analyst agent
    analyst = AnalystAgent(queue, llm, pdf_reader)
    
    print(f"✅ {analyst.name} initialized")
    print(f"   Role: {analyst.role}")
    print()


    # Test with a sample paper (you'll need to provide path)
    print("📄 To test, provide path to a PDF research paper:")
    paper_path = input("Enter path (or press Enter to skip): ").strip()
    
    if paper_path:
        # Create a test message
        test_message = Message(
            sender="tester",
            recipient="analyst",
            message_type=MessageType.REQUEST,
            content={
                'action': 'analyze',
                'paper_path': paper_path
            }
        )
        
        # Process
        result = analyst.process(test_message)
        
        print("\n" + "="*60)
        print("📊 ANALYSIS RESULT")
        print("="*60)
        print(json.dumps(result, indent=2))
    else:
        print("⏭️  Skipping test (no paper provided)")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo_analyst()
