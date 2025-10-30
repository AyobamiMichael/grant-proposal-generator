
"""
agents/innovator_agent.py
Generate novel research directions and extensions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo_phase1 import BaseAgent, Message, MessageType
from typing import Dict, Any
import json

class InnovatorAgent(BaseAgent):
    """
    Innovator Agent - Creative Research Extension
    
    Role: Identify future directions & applications
    Personality: Visionary, creative, forward-thinking
    
    Capabilities:
    - Generate 3-5 novel research directions
    - Identify potential industry applications
    - Propose extensions to current work
    - Suggest cross-disciplinary connections
    - Create "what if" scenarios
    - Assess commercial potential
    """

    def __init__(self, message_queue, llm):
        super().__init__(
            name="innovator",
            role="Creative Research Extension & Future Directions",
            message_queue=message_queue
        )
        self.llm = llm
    
    def process(self, message: Message) -> Dict[str, Any]:
        """
        Process innovation request
        
        Expected message content:
        {
            'action': 'innovate',
            'analysis': {...},  # From analyst
            'evaluation': {...}  # From evaluator
        }

         Returns:
        {
            'future_directions': [...],
            'industry_applications': [...],
            'extensions': [...],
            'cross_disciplinary': [...],
            'commercial_potential': 'HIGH' | 'MEDIUM' | 'LOW',
            'ten_year_vision': '...',
            'breakthrough_potential': {...}
        }
        """
        action = message.content.get('action')
        
        if action != 'innovate':
            return {'error': f'Unknown action: {action}'}
        
        analysis = message.content.get('analysis')
        evaluation = message.content.get('evaluation')
        
        if not analysis:
            return {'error': 'No analysis provided'}
        
        print(f"💡 Innovator: Generating future directions...")

        try:
            # Generate innovations
            innovations = self._generate_innovations(analysis, evaluation)
            
            print(f"✅ Innovator: Generated {len(innovations.get('future_directions', []))} future directions")
            print(f"   Commercial Potential: {innovations.get('commercial_potential', 'N/A')}")
            
            return innovations
            
        except Exception as e:
            print(f"❌ Innovator error: {e}")
            return {'error': str(e)}
    
    def _generate_innovations(
        self,
        analysis: Dict[str, Any],
        evaluation: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Use LLM to generate innovative directions"""
        
        print("🧠 Innovator: Calling LLM for creative ideation...")
        
        # Build innovation prompt
        prompt = f"""You are a visionary research innovator. Based on this paper analysis, generate creative future directions.

PAPER ANALYSIS:
Title: {analysis.get('title', 'Unknown')}
Key Contributions: {json.dumps(analysis.get('key_contributions', []), indent=2)}
Methodology: {json.dumps(analysis.get('methodology', {}), indent=2)}
Results: {json.dumps(analysis.get('main_results', {}), indent=2)}
Limitations: {json.dumps(analysis.get('limitations', []), indent=2)}
Gaps: {json.dumps(analysis.get('gaps_identified', []), indent=2)}

Generate innovative extensions and directions:


1. **Future Research Directions** (3-5 specific directions):
   - What are the most promising unexplored areas?
   - What novel variations could be investigated?
   - What fundamental questions remain?

2. **Industry Applications** (3-5 real-world applications):
   - Healthcare, finance, education, manufacturing, etc.
   - Specific use cases with clear value
   - Near-term vs long-term opportunities

3. **Novel Extensions** (3-5 technical extensions):
   - Algorithmic improvements
   - New architectures or approaches
   - Combining with other techniques
   - Scaling to new domains

4. **Cross-Disciplinary Connections** (2-4 connections):
   - How could this intersect with biology, physics, social science, etc.?
   - Unexpected applications in other fields
   - Potential for interdisciplinary breakthroughs

5. **Commercial Potential**: HIGH / MEDIUM / LOW
   - Can this be monetized?
   - Market size and demand
   - Competitive advantages

6. **10-Year Vision**:
   - Where could this research lead in a decade?
   - Transformative potential
   - Societal impact

7. **Breakthrough Potential**:
   - Could this lead to major breakthroughs?
   - Nobel Prize potential? (be honest)
   - Paradigm-shifting capability

Be creative, ambitious, and forward-thinking. Think like a visionary researcher who sees beyond current limitations."""
        
        # Define expected schema
        schema = {
            "future_directions": [
                {
                    "direction": "string (title)",
                    "description": "string (2-3 sentences)",
                    "feasibility": "HIGH | MEDIUM | LOW",
                    "timeframe": "string (1-2 years, 3-5 years, 5-10 years)"
                }
            ],
            "industry_applications": [
                {
                    "domain": "string (industry/field)",
                    "application": "string (specific use case)",
                    "value_proposition": "string",
                    "readiness": "string (ready now, 1-2 years, 3-5 years)"
                }
            ],
            "extensions": [
                {
                    "extension": "string (title)",
                    "description": "string",
                    "technical_challenge": "string"
                }
            ],
            "cross_disciplinary": [
                {
                    "field": "string",
                    "connection": "string",
                    "potential": "string"
                }
            ],
            "commercial_potential": "HIGH | MEDIUM | LOW",
            "commercial_reasoning": "string",
            "ten_year_vision": "string (paragraph)",
            "breakthrough_potential": {
                "score": "number (0-10)",
                "reasoning": "string",
                "paradigm_shift": "boolean"
            }
        }

          # Call LLM
        try:
            innovations = self.llm.generate_structured(
                prompt=prompt,
                schema=schema,
                max_tokens=3000,
                temperature=0.8  # Higher for creativity
            )
            
            print(f"✅ Innovator: LLM ideation successful")
            
            return innovations
            
        except Exception as e:
            print(f"❌ Innovator LLM error: {e}")
            
            # Return fallback
            return {
                'future_directions': [
                    {
                        'direction': 'Could not generate',
                        'description': f'Ideation failed: {str(e)}',
                        'feasibility': 'UNKNOWN',
                        'timeframe': 'Unknown'
                    }
                ],
                'industry_applications': [],
                'extensions': [],
                'cross_disciplinary': [],
                'commercial_potential': 'UNKNOWN',
                'commercial_reasoning': f'Error: {str(e)}',
                'ten_year_vision': 'Could not generate vision',
                'breakthrough_potential': {
                    'score': 0,
                    'reasoning': f'Generation failed: {str(e)}',
                    'paradigm_shift': False
                },
                'error': str(e)
            }
    def generate_what_if_scenarios(self, analysis: Dict[str, Any]) -> list:
        """Generate creative 'what if' scenarios"""
        
        print("🔮 Innovator: Generating 'what if' scenarios...")
        
        prompt = f"""Based on this research, generate 5 creative "what if" scenarios:

Research: {analysis.get('title', 'Unknown')}
Contributions: {json.dumps(analysis.get('key_contributions', []))}

Generate 5 "what if" scenarios exploring:
1. What if this technique was 100x faster?
2. What if it could handle 1000x more data?
3. What if it was combined with [emerging technology]?
4. What if the assumptions were changed?
5. What if it was applied to [unexpected domain]?

Make them specific, creative, and thought-provoking."""
        

        try:
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=800,
                temperature=0.9  # Very creative
            )
            
            # Parse scenarios
            scenarios = [s.strip() for s in response.split('\n') if s.strip()]
            return scenarios[:5]
            
        except Exception as e:
            print(f"❌ Scenario generation error: {e}")
            return ["Could not generate scenarios due to error"]
    
    def assess_funding_opportunities(
        self,
        innovations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify potential funding opportunities"""
        
        print("💰 Innovator: Identifying funding opportunities...")
        
        prompt = f"""Based on these research innovations, identify funding opportunities:

INNOVATIONS:
{json.dumps(innovations, indent=2)}

Identify:
1. **Relevant Funding Agencies**:
   - NSF programs (specific)
   - NIH if applicable
   - DARPA if defense-related
   - Private foundations
   - Industry partnerships

2. **Grant Types**:
   - Small grants ($50K-$250K)
   - Medium grants ($250K-$1M)
   - Large grants ($1M+)

3. **Best Fit Programs** (top 3):
   - Program name
   - Why it's a good fit
   - Typical funding amount

4. **Funding Timeline**:
   - When to apply
   - Competition level"""
        
        schema = {
            "funding_agencies": ["string"],
            "grant_types": {
                "small_grants": ["string"],
                "medium_grants": ["string"],
                "large_grants": ["string"]
            },
            "best_fit_programs": [
                {
                    "program": "string",
                    "agency": "string",
                    "fit_reasoning": "string",
                    "typical_amount": "string"
                }
            ],
            "recommended_timeline": "string"
        }
        
        try:
            opportunities = self.llm.generate_structured(
                prompt=prompt,
                schema=schema,
                max_tokens=1500,
                temperature=0.5
            )
            
            return opportunities
            
        except Exception as e:
            return {
                'funding_agencies': [],
                'grant_types': {},
                'best_fit_programs': [],
                'recommended_timeline': 'Unknown',
                'error': str(e)
            }
    
    def generate_collaboration_network(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Suggest potential collaborators and interdisciplinary connections"""
        
        print("🤝 Innovator: Mapping collaboration opportunities...")
        
        prompt = f"""Based on this research, suggest collaboration opportunities:

Research: {analysis.get('title', 'Unknown')}
Field: Based on {json.dumps(analysis.get('methodology', {}))}

Suggest:
1. **Complementary Expertise Needed** (3-5):
   - What skills/knowledge would enhance this?
   - Specific expertise areas

2. **Potential Collaborator Types**:
   - Academic departments
   - Research labs
   - Industry partners
   - Government agencies

3. **Interdisciplinary Opportunities**:
   - Fields to connect with
   - Synergies and benefits

4. **International Collaboration**:
   - Countries/regions with relevant expertise
   - Global research networks"""
        
        try:
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.6
            )
            
            return {
                'collaboration_suggestions': response,
                'generated': True
            }
            
        except Exception as e:
            return {
                'collaboration_suggestions': 'Could not generate',
                'error': str(e)
            }

# ==================== DEMO ====================

def demo_innovator():
    """Demo the Innovator Agent"""
    
    print("="*60)
    print("💡 INNOVATOR AGENT DEMO")
    print("="*60)
    print()
    
    # Initialize dependencies
    from tools.llm_wrapper import LLMWrapper
    from demo_phase1 import MessageQueue
    
    llm = LLMWrapper(model='fast')
    queue = MessageQueue()
    
    # Create innovator agent
    innovator = InnovatorAgent(queue, llm)
    
    print(f"✅ {innovator.name} initialized")
    print(f"   Role: {innovator.role}")
    print()

     # Mock analysis from previous agents
    mock_analysis = {
        'title': 'Attention Is All You Need',
        'key_contributions': [
            'Introduced Transformer architecture',
            'Eliminated recurrence with self-attention',
            'Achieved SOTA on translation'
        ],
        'methodology': {
            'approach': 'Multi-head self-attention',
            'datasets': ['WMT 2014'],
            'evaluation_metrics': ['BLEU']
        },
        'main_results': {
            'summary': 'Best translation performance',
            'performance_improvements': ['28.4 BLEU on EN-DE']
        },
        'limitations': [
            'O(n²) memory complexity',
            'Requires large datasets'
        ],
        'gaps_identified': [
            'Efficiency for long sequences',
            'Applications beyond NLP'
        ]
    }
    
    # Create test message
    test_message = Message(
        sender="supervisor",
        recipient="innovator",
        message_type=MessageType.REQUEST,
        content={
            'action': 'innovate',
            'analysis': mock_analysis
        }
    )

     # Process
    print("🧪 Generating innovations for Transformer paper...")
    print()
    
    result = innovator.process(test_message)
    
    print("\n" + "="*60)
    print("💡 INNOVATION RESULTS")
    print("="*60)
    
    if 'error' not in result:
        print(f"\n🚀 Future Directions ({len(result.get('future_directions', []))}):")
        for i, direction in enumerate(result.get('future_directions', [])[:3], 1):
            print(f"\n{i}. {direction.get('direction', 'N/A')}")
            print(f"   {direction.get('description', 'N/A')}")
            print(f"   Feasibility: {direction.get('feasibility', 'N/A')}")
            print(f"   Timeframe: {direction.get('timeframe', 'N/A')}")
        
        print(f"\n🏭 Industry Applications ({len(result.get('industry_applications', []))}):")
        for i, app in enumerate(result.get('industry_applications', [])[:3], 1):
            print(f"\n{i}. {app.get('domain', 'N/A')}: {app.get('application', 'N/A')}")
            print(f"   Value: {app.get('value_proposition', 'N/A')}")
        
        print(f"\n💰 Commercial Potential: {result.get('commercial_potential', 'N/A')}")
        print(f"   {result.get('commercial_reasoning', 'N/A')}")
        
        print(f"\n🔮 10-Year Vision:")
        print(f"   {result.get('ten_year_vision', 'N/A')}")
        
        breakthrough = result.get('breakthrough_potential', {})
        print(f"\n⭐ Breakthrough Potential: {breakthrough.get('score', 0)}/10")
        print(f"   {breakthrough.get('reasoning', 'N/A')}")
        print(f"   Paradigm Shift: {breakthrough.get('paradigm_shift', False)}")
    else:
        print(f"\n❌ Error: {result['error']}")
    
    print("\n" + "="*60)
    print("📋 FULL OUTPUT (JSON)")
    print("="*60)
    print(json.dumps(result, indent=2))
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo_innovator()