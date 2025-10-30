"""
agents/writer_agent.py
Synthesize all agent outputs into grant proposal
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from demo_phase1 import BaseAgent, Message, MessageType
from typing import Dict, Any
import json
from datetime import datetime

class WriterAgent(BaseAgent):
    """
    Writer Agent - Grant Proposal Synthesis
    
    Role: Create final grant proposal document
    Personality: Eloquent, persuasive, policy-aware
    
    Capabilities:
    - Synthesize all agent outputs into coherent narrative
    - Write NSF/NIH-style grant proposal sections
    - Handle conflicts between agents
    - Generate executive summary
    - Create research plan and timeline
    - Write impact statement
    - Format professional proposal
    """
    def __init__(self, message_queue, llm):
        super().__init__(
            name="writer",
            role="Grant Proposal Synthesis & Document Generation",
            message_queue=message_queue
        )
        self.llm = llm

    def process(self, message: Message) -> Dict[str, Any]:
        """
        Process writing request
        
        Expected message content:
        {
            'action': 'write_proposal',
            'analysis': {...},      # From analyst
            'evaluation': {...},    # From evaluator
            'innovations': {...},   # From innovator
            'conflicts': [...]      # Optional: any conflicts
        }
        
         Returns:
        {
            'proposal': {
                'executive_summary': '...',
                'project_description': '...',
                'research_plan': '...',
                'broader_impacts': '...',
                'budget_justification': '...',
                'timeline': {...}
            },
            'full_text': '...',  # Complete formatted proposal
            'word_count': int,
            'metadata': {...}
        }
        """
        action = message.content.get('action')

         
        if action != 'write_proposal':
            return {'error': f'Unknown action: {action}'}
        
        analysis = message.content.get('analysis')
        evaluation = message.content.get('evaluation')
        innovations = message.content.get('innovations')
        conflicts = message.content.get('conflicts', [])

        if not analysis or not evaluation or not innovations:
            return {'error': 'Missing required inputs (analysis, evaluation, or innovations)'}
        
        print(f"✍️  Writer: Synthesizing grant proposal...")

        try:
            # Generate proposal
            proposal = self._write_proposal(
                analysis=analysis,
                evaluation=evaluation,
                innovations=innovations,
                conflicts=conflicts
            )
            
            word_count = len(proposal.get('full_text', '').split())
            
            print(f"✅ Writer: Proposal complete ({word_count} words)")
            
            return proposal
        
        except Exception as e:
            print(f"❌ Writer error: {e}")
            return {'error': str(e)}
    
    def _write_proposal(
        self,
        analysis: Dict[str, Any],
        evaluation: Dict[str, Any],
        innovations: Dict[str, Any],
        conflicts: list
    ) -> Dict[str, Any]:
        """Generate complete grant proposal"""
        
        print("🧠 Writer: Generating proposal sections...")
        
        # Generate each section
        sections = {}
        
        # 1. Executive Summary
        print("   📝 Writing executive summary...")
        sections['executive_summary'] = self._write_executive_summary(
            analysis, evaluation, innovations
        )
        
        # 2. Project Description
        print("   📝 Writing project description...")
        sections['project_description'] = self._write_project_description(
            analysis, evaluation
        )

        # 3. Research Plan
        print("   📝 Writing research plan...")
        sections['research_plan'] = self._write_research_plan(
            analysis, innovations
        )

        # 4. Broader Impacts
        print("   📝 Writing broader impacts...")
        sections['broader_impacts'] = self._write_broader_impacts(
            innovations
        )

        # 5. Budget Justification
        print("   📝 Writing budget justification...")
        sections['budget_justification'] = self._write_budget_justification(
            innovations
        )

         # 6. Timeline
        print("   📝 Creating timeline...")
        sections['timeline'] = self._create_timeline(innovations)
        
        # 7. References (placeholder)
        sections['references'] = self._create_references(analysis)
        
        # Assemble full proposal
        full_text = self._assemble_proposal(sections, analysis)
        
        # Handle conflicts if any
        if conflicts:
            conflict_resolution = self._resolve_conflicts(conflicts)
            sections['conflict_resolution'] = conflict_resolution
        
        return {
            'proposal': sections,
            'full_text': full_text,
            'word_count': len(full_text.split()),
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'paper_title': analysis.get('title', 'Unknown'),
                'quality_score': evaluation.get('scores', {}).get('overall', 0),
                'funding_potential': evaluation.get('funding_potential', 'UNKNOWN'),
                'conflicts_resolved': len(conflicts)
            }
        }
    
    def _write_executive_summary(
        self,
        analysis: Dict,
        evaluation: Dict,
        innovations: Dict
    ) -> str:
        """Generate executive summary (1 page)"""
        
        prompt = f"""Write a compelling 1-page executive summary for a grant proposal based on:

PAPER: {analysis.get('title', 'Unknown')}

KEY FINDINGS:
{json.dumps(analysis.get('key_contributions', []), indent=2)}

QUALITY ASSESSMENT:
Overall Score: {evaluation.get('scores', {}).get('overall', 0)}/10
Funding Potential: {evaluation.get('funding_potential', 'UNKNOWN')}

FUTURE DIRECTIONS:
{json.dumps([d.get('direction') for d in innovations.get('future_directions', [])], indent=2)}

Write an executive summary (250-300 words) that:
1. Opens with a compelling hook about the problem
2. Summarizes the key innovation
3. Highlights intellectual merit
4. Emphasizes broader impacts
5. States funding request (assume $500K over 3 years)
6. Ends with transformative potential

Use persuasive, professional grant-writing style. Make it exciting but credible."""

        try:
            summary = self.llm.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            return summary.strip()
        except Exception as e:
            return f"[Executive Summary - Generation Error: {e}]"

    def _write_project_description(
        self,
        analysis: Dict,
        evaluation: Dict
    ) -> str:
        """Generate project description (2-3 pages)"""
        prompt = f"""Write a detailed project description for a grant proposal:
        
PAPER ANALYSIS:
Title: {analysis.get('title')}
Contributions: {json.dumps(analysis.get('key_contributions', []))}
Methodology: {json.dumps(analysis.get('methodology', {}))}
Results: {json.dumps(analysis.get('main_results', {}))}

EVALUATION:
Strengths: {json.dumps(evaluation.get('strengths', []))}
Weaknesses: {json.dumps(evaluation.get('weaknesses', []))}

Write 3-4 paragraphs covering:
1. **Background & Motivation**: Why is this important?
2. **Current State**: What has been done (cite the paper)?
3. **Gap & Opportunity**: What's missing and why it matters
4. **Proposed Work**: What we will do to address the gap

Use clear, compelling academic writing. Be specific about technical details."""
        
        try:
            description = self.llm.generate(
                prompt=prompt,
                max_tokens=800,
                temperature=0.6
            )
            return description.strip()
        except Exception as e:
            return f"[Project Description - Generation Error: {e}]"
        
    def _write_research_plan(
        self,
        analysis: Dict,
        innovations: Dict
    ) -> str:
        """Generate research plan with specific aims"""
        
        prompt = f"""Write a detailed research plan with specific aims:
CURRENT WORK:
{json.dumps(analysis.get('key_contributions', []))}

FUTURE DIRECTIONS:
{json.dumps([{
    'direction': d.get('direction'),
    'description': d.get('description'),
    'feasibility': d.get('feasibility')
} for d in innovations.get('future_directions', [])[:3]], indent=2)}

EXTENSIONS:
{json.dumps([e.get('extension') for e in innovations.get('extensions', [])], indent=2)}

Structure:

**Aim 1: [First Direction]**
- Rationale (why important)
- Approach (how we'll do it)
- Expected outcomes
- Potential challenges and mitigation

**Aim 2: [Second Direction]**
- (same structure)

**Aim 3: [Third Direction]**
- (same structure)

Write 2-3 paragraphs per aim. Be specific and technical."""
        
        try:
            plan = self.llm.generate(
                prompt=prompt,
                max_tokens=1200,
                temperature=0.6
            )
            return plan.strip()
        except Exception as e:
            return f"[Research Plan - Generation Error: {e}]"
    
    def _write_broader_impacts(self, innovations: Dict) -> str:
        """Generate broader impacts statement"""
        
        prompt = f"""Write a compelling broader impacts statement:

APPLICATIONS:
{json.dumps([{
    'domain': a.get('domain'),
    'application': a.get('application'),
    'value': a.get('value_proposition')
} for a in innovations.get('industry_applications', [])], indent=2)}

COMMERCIAL POTENTIAL: {innovations.get('commercial_potential')}

VISION:
{innovations.get('ten_year_vision', '')}

Write 2-3 paragraphs covering:
1. **Societal Impact**: How will this benefit society?
2. **Educational Impact**: Training, outreach, diversity
3. **Economic Impact**: Jobs, innovation, competitiveness
4. **Global Impact**: International collaboration, sustainability

Be aspirational but realistic. Show transformative potential."""
        
        try:
            impacts = self.llm.generate(
                prompt=prompt,
                max_tokens=600,
                temperature=0.7
            )
            return impacts.strip()
        except Exception as e:
            return f"[Broader Impacts - Generation Error: {e}]"
    

    def _write_budget_justification(self, innovations: Dict) -> str:
        """Generate budget justification"""
        
        # Simple template budget
        budget_template = """
BUDGET JUSTIFICATION (3-Year Project, $500,000 Total)

**Year 1: $180,000**
- Personnel: $120,000 (PI 1 month summer, 1 Postdoc, 1 PhD student)
- Equipment: $30,000 (GPU cluster, software licenses)
- Travel: $15,000 (Conference presentations, collaborations)
- Other: $15,000 (Cloud computing, datasets, publication fees)

**Year 2: $160,000**
- Personnel: $125,000 (Same team, cost-of-living adjustment)
- Equipment: $10,000 (Additional computing resources)
- Travel: $15,000 (Conferences, workshops)
- Other: $10,000 (Materials, services)

**Year 3: $160,000**
- Personnel: $130,000 (Same team structure)
- Travel: $20,000 (Final dissemination, collaborations)
- Other: $10,000 (Publication, open-source release)

**Justification:**
This budget supports a lean, focused team to achieve the proposed aims. The postdoc
will lead implementation, the PhD student will conduct experiments, and the PI will
provide strategic direction. Equipment costs are essential for computational research.
Travel enables dissemination and collaboration with key partners."""
        
        return budget_template.strip()
    
    def _create_timeline(self, innovations: Dict) -> Dict[str, list]:
        """Create project timeline"""
        
        timeline = {
            'Year 1': [
                'Q1: Literature review and baseline implementation',
                'Q2: Aim 1 - Initial experiments and data collection',
                'Q3: Aim 1 - Analysis and refinement',
                'Q4: Aim 2 - Begin second direction'
            ],
            'Year 2': [
                'Q1: Aim 2 - Core development',
                'Q2: Aim 2 - Testing and validation',
                'Q3: Aim 3 - Begin third direction',
                'Q4: Integration and cross-validation'
            ],
            'Year 3': [
                'Q1: Comprehensive evaluation',
                'Q2: Real-world deployment and testing',
                'Q3: Paper writing and submission',
                'Q4: Open-source release and dissemination'
            ]
        }
        
        return timeline
    def _create_references(self, analysis: Dict) -> str:
        """Create references section (placeholder)"""
        
        # In real implementation, would extract from PDF
        refs = f"""
REFERENCES

[1] {', '.join(analysis.get('authors', ['Unknown']))}. "{analysis.get('title', 'Unknown')}". 
    {analysis.get('venue', 'Conference/Journal')}, {analysis.get('year', 'Year')}.

[2-10] Additional references would be extracted from the paper and added here...
"""
        return refs.strip()
    

    def _resolve_conflicts(self, conflicts: list) -> str:
        """Generate conflict resolution explanation"""
        
        if not conflicts:
            return "No conflicts to resolve."
        
        prompt = f"""These agents disagreed during analysis:

{json.dumps(conflicts, indent=2)}

Write a brief paragraph explaining:
1. What the disagreement was
2. How we resolved it (weighted expert opinions, additional analysis, etc.)
3. Why the final decision is sound

Be diplomatic and show that diverse perspectives strengthen the proposal."""
        
        try:
            resolution = self.llm.generate(
                prompt=prompt,
                max_tokens=300,
                temperature=0.6
            )
            return resolution.strip()
        except Exception as e:
            return f"[Conflict resolution failed: {e}]"
    

    def _assemble_proposal(self, sections: Dict, analysis: Dict) -> str:
        """Assemble all sections into formatted proposal"""
        
        proposal = f"""
{'='*70}
GRANT PROPOSAL
{'='*70}

Title: Extension and Application of "{analysis.get('title', 'Unknown')}"
Principal Investigator: [PI Name]
Institution: [Institution]
Duration: 3 years
Requested Amount: $500,000

{'='*70}

EXECUTIVE SUMMARY
{'-'*70}
{sections.get('executive_summary', '[Missing]')}

{'='*70}

PROJECT DESCRIPTION
{'-'*70}
{sections.get('project_description', '[Missing]')}

{'='*70}

RESEARCH PLAN
{'-'*70}
{sections.get('research_plan', '[Missing]')}

{'='*70}

BROADER IMPACTS
{'-'*70}
{sections.get('broader_impacts', '[Missing]')}

{'='*70}

BUDGET JUSTIFICATION
{'-'*70}
{sections.get('budget_justification', '[Missing]')}

{'='*70}

PROJECT TIMELINE
{'-'*70}
"""
        
        # Add timeline
        timeline = sections.get('timeline', {})
        for year, quarters in timeline.items():
            proposal += f"\n{year}:\n"
            for quarter in quarters:
                proposal += f"  • {quarter}\n"
        
        proposal += f"\n{'='*70}\n"
        proposal += f"\nREFERENCES\n{'-'*70}\n"
        proposal += sections.get('references', '[Missing]')
        
        proposal += f"\n\n{'='*70}\n"
        proposal += f"END OF PROPOSAL\n"
        proposal += f"{'='*70}\n"
        
        return proposal
    


# ==================== DEMO ====================

def demo_writer():
    """Demo the Writer Agent"""
    
    print("="*60)
    print("✍️  WRITER AGENT DEMO")
    print("="*60)
    print()
    
    # Initialize dependencies
    from tools.llm_wrapper import LLMWrapper
    from demo_phase1 import MessageQueue
    
    llm = LLMWrapper(model='fast')
    queue = MessageQueue()
    
    # Create writer agent
    writer = WriterAgent(queue, llm)
    
    print(f"✅ {writer.name} initialized")
    print(f"   Role: {writer.role}")
    print()
    
    # Mock inputs from other agents
    mock_data = {
        'analysis': {
            'title': 'Attention Is All You Need',
            'authors': ['Vaswani et al.'],
            'year': 2017,
            'venue': 'NeurIPS',
            'key_contributions': [
                'Introduced Transformer architecture',
                'Eliminated recurrence',
                'Achieved SOTA translation'
            ],
            'methodology': {
                'approach': 'Self-attention mechanism',
                'datasets': ['WMT 2014']
            },
            'main_results': {
                'summary': 'Best translation performance',
                'performance_improvements': ['28.4 BLEU']
            }
        },
        'evaluation': {
            'scores': {'overall': 9},
            'funding_potential': 'HIGH',
            'strengths': ['Novel architecture', 'Strong results'],
            'weaknesses': ['Memory complexity']
        },
        'innovations': {
            'future_directions': [
                {
                    'direction': 'Efficient attention mechanisms',
                    'description': 'Reduce O(n²) complexity',
                    'feasibility': 'HIGH'
                }
            ],
            'industry_applications': [
                {
                    'domain': 'Healthcare',
                    'application': 'Medical text analysis',
                    'value_proposition': 'Faster diagnosis'
                }
            ],
            'extensions': [{'extension': 'Sparse attention'}],
            'commercial_potential': 'HIGH',
            'ten_year_vision': 'Ubiquitous AI translation'
        }
    }
    
    # Create test message
    test_message = Message(
        sender="supervisor",
        recipient="writer",
        message_type=MessageType.REQUEST,
        content={
            'action': 'write_proposal',
            **mock_data
        }
    )
    
    # Process
    print("🧪 Generating grant proposal...")
    print()
    
    result = writer.process(test_message)
    
    print("\n" + "="*60)
    print("✍️  PROPOSAL GENERATED")
    print("="*60)
    
    if 'error' not in result:
        print(f"\n📊 Metadata:")
        metadata = result.get('metadata', {})
        for key, value in metadata.items():
            print(f"   {key}: {value}")
        
        print(f"\n📄 Proposal Preview (first 1000 chars):")
        print("-" * 60)
        full_text = result.get('full_text', '')
        print(full_text[:1000])
        print("...\n[truncated]\n")
        
        # Option to save
        save = input("Save full proposal to file? (y/n): ").strip().lower()
        if save == 'y':
            filename = "grant_proposal.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(full_text)
            print(f"✅ Saved to {filename}")
    else:
        print(f"\n❌ Error: {result['error']}")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo_writer()