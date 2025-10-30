"""
agents/evaluator_agent.py
Assess paper quality and funding potential
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo_phase1 import BaseAgent, Message, MessageType
from typing import Dict, Any
import json


class EvaluatorAgent(BaseAgent):
    """
    Evaluator Agent - Paper Quality Assessment & Review
    
    Role: Assess paper quality and impact potential
    Personality: Critical but fair, peer-review style
    
    Capabilities:
    - Score originality, methodology, and impact
    - Identify weaknesses in approach
    - Assess funding potential
    - Generate reviewer-style feedback
    - Compare to state-of-the-art
    """

    def __init__(self, message_queue, llm):
        super().__init__(
            name="evaluator",
            role="Paper Quality Assessment & Review",
            message_queue=message_queue
        )
        self.llm = llm

    def process(self, message: Message) -> Dict[str, Any]:
        """
        Process evaluation request
        
        Expected message content:
        {
            'action': 'evaluate',
            'analysis': {... analyst output ...}
        }
        
        Returns:
        {
            'scores': {
                'originality': 0-10,
                'methodology': 0-10,
                'impact': 0-10,
                'clarity': 0-10,
                'overall': 0-10
            },
            'funding_potential': 'HIGH' | 'MEDIUM' | 'LOW',
            'strengths': [...],
            'weaknesses': [...],
            'reviewer_feedback': [...],
            'recommendations': {...}
        }
        """
        action = message.content.get('action')
        
        if action != 'evaluate':
            return {'error': f'Unknown action: {action}'}
        
        analysis = message.content.get('analysis')
        
        if not analysis:
            return {'error': 'No analysis provided'}
        
        print(f"⚖️ Evaluator: Assessing paper quality...")
        
        try:
            # Evaluate the paper
            evaluation = self._evaluate_paper(analysis)
            
            print(f"✅ Evaluator: Evaluation complete")
            print(f"   Overall Score: {evaluation.get('scores', {}).get('overall', 0)}/10")
            print(f"   Funding Potential: {evaluation.get('funding_potential', 'UNKNOWN')}")
            
            return evaluation
            
        except Exception as e:
            print(f"❌ Evaluator error: {e}")
            return {'error': str(e)}
    
    def _evaluate_paper(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to evaluate paper quality"""
        
        print("🧠 Evaluator: Calling LLM for evaluation...")
        
        # Build evaluation prompt
        prompt = f"""You are a peer reviewer evaluating this research paper. Provide a thorough assessment.

PAPER ANALYSIS:
{json.dumps(analysis, indent=2)}

Evaluate the paper on these dimensions:

1. **Originality** (0-10): How novel is this work?
   - Are the ideas new?
   - Does it advance the field?
   - Is it incremental or groundbreaking?

2. **Methodology** (0-10): How sound is the approach?
   - Is the method well-designed?
   - Are experiments rigorous?
   - Are datasets appropriate?
   - Are comparisons fair?

3. **Impact** (0-10): What is the potential impact?
   - Will this influence future research?
   - Are there practical applications?
   - Is it significant for the community?

4. **Clarity** (0-10): How well is it presented?
   - Is the writing clear?
   - Are results well-explained?
   - Is it reproducible?

5. **Overall** (0-10): Overall quality assessment

Additionally provide:
- **Funding Potential**: HIGH / MEDIUM / LOW (would this get funded?)
- **Strengths**: 3-5 key strengths
- **Weaknesses**: 3-5 key weaknesses or concerns
- **Reviewer Feedback**: 3-5 critical comments (peer-review style)
- **Recommendations**: What needs improvement for acceptance/funding?

Be critical but constructive. Think like a senior researcher reviewing for a top conference."""
        
        # Define expected schema
        schema = {
            "scores": {
                "originality": "number (0-10)",
                "methodology": "number (0-10)",
                "impact": "number (0-10)",
                "clarity": "number (0-10)",
                "overall": "number (0-10)"
            },
            "funding_potential": "HIGH | MEDIUM | LOW",
            "strengths": ["string"],
            "weaknesses": ["string"],
            "reviewer_feedback": ["string"],
            "recommendations": {
                "for_publication": ["string"],
                "for_funding": ["string"],
                "future_work": ["string"]
            },
            "decision_reasoning": "string"
        }
        
        # Call LLM
        try:
            evaluation = self.llm.generate_structured(
                prompt=prompt,
                schema=schema,
                max_tokens=2000,
                temperature=0.4  # Balanced for thoughtful evaluation
            )
            
            print(f"✅ Evaluator: LLM evaluation successful")
            
            # Validate scores are in range
            for score_name, score in evaluation['scores'].items():
                if not (0 <= score <= 10):
                    print(f"⚠️ Warning: {score_name} score out of range: {score}")
                    evaluation['scores'][score_name] = max(0, min(10, score))
            
            return evaluation
            
        except Exception as e:
            print(f"❌ Evaluator LLM error: {e}")
            
            # Return fallback evaluation
            return {
                'scores': {
                    'originality': 0,
                    'methodology': 0,
                    'impact': 0,
                    'clarity': 0,
                    'overall': 0
                },
                'funding_potential': 'UNKNOWN',
                'strengths': [],
                'weaknesses': [f'Evaluation failed: {str(e)}'],
                'reviewer_feedback': [f'Could not complete evaluation: {str(e)}'],
                'recommendations': {
                    'for_publication': [],
                    'for_funding': [],
                    'future_work': []
                },
                'decision_reasoning': f'Evaluation error: {str(e)}',
                'error': str(e)
            }
        
    def compare_to_baseline(
        self,
        analysis: Dict[str, Any],
        baseline_description: str
    ) -> Dict[str, Any]:
        """Compare paper to a baseline or state-of-the-art"""
        
        print("📊 Evaluator: Comparing to baseline...")
        
        prompt = f"""Compare this paper to the baseline/state-of-the-art:

PAPER RESULTS:
{json.dumps(analysis.get('main_results', {}), indent=2)}

BASELINE:
{baseline_description}

Provide comparison:
1. How does this paper improve over baseline?
2. What are the performance gains?
3. Is the comparison fair?
4. What are the limitations of the comparison?

Be specific about quantitative improvements if mentioned."""
        
        try:
            comparison = self.llm.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.5
            )
            
            return {
                'comparison_summary': comparison,
                'baseline': baseline_description
            }
            
        except Exception as e:
            return {
                'comparison_summary': f'Comparison failed: {str(e)}',
                'error': str(e)
            }
    
    def assess_reproducibility(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how reproducible the work is"""
        
        print("🔬 Evaluator: Assessing reproducibility...")
        
        methodology = analysis.get('methodology', {})
        
        prompt = f"""Assess the reproducibility of this research:

METHODOLOGY:
{json.dumps(methodology, indent=2)}

DATASETS: {methodology.get('datasets', [])}
EVALUATION METRICS: {methodology.get('evaluation_metrics', [])}

Rate reproducibility (0-10) and identify:
1. What information is provided?
2. What is missing for reproduction?
3. Are code/data available? (if mentioned)
4. Can someone else replicate this?

Provide:
- reproducibility_score (0-10)
- available_resources (list)
- missing_information (list)
- reproducibility_notes (string)"""
        
        schema = {
            "reproducibility_score": "number (0-10)",
            "available_resources": ["string"],
            "missing_information": ["string"],
            "reproducibility_notes": "string"
        }
        
        try:
            assessment = self.llm.generate_structured(
                prompt=prompt,
                schema=schema,
                temperature=0.3
            )
            
            return assessment
            
        except Exception as e:
            return {
                'reproducibility_score': 0,
                'available_resources': [],
                'missing_information': [f'Assessment error: {str(e)}'],
                'reproducibility_notes': 'Could not assess',
                'error': str(e)
            }
    
    def generate_review_summary(self, evaluation: Dict[str, Any]) -> str:
        """Generate a concise review summary"""
        
        scores = evaluation.get('scores', {})
        funding = evaluation.get('funding_potential', 'UNKNOWN')
        
        summary = f"""REVIEW SUMMARY
{"="*50}

Overall Score: {scores.get('overall', 0)}/10
Funding Potential: {funding}

Scores:
- Originality: {scores.get('originality', 0)}/10
- Methodology: {scores.get('methodology', 0)}/10
- Impact: {scores.get('impact', 0)}/10
- Clarity: {scores.get('clarity', 0)}/10

STRENGTHS:
"""
        
        for i, strength in enumerate(evaluation.get('strengths', []), 1):
            summary += f"{i}. {strength}\n"
        
        summary += "\nWEAKNESSES:\n"
        for i, weakness in enumerate(evaluation.get('weaknesses', []), 1):
            summary += f"{i}. {weakness}\n"
        
        summary += f"\nDECISION: {evaluation.get('decision_reasoning', 'N/A')}"
        
        return summary
    

# ==================== DEMO ====================

def demo_evaluator():
    """Demo the Evaluator Agent"""
    
    print("="*60)
    print("⚖️ EVALUATOR AGENT DEMO")
    print("="*60)
    print()
    
    # Initialize dependencies
    from llm_wrapper import LLMWrapper
    from demo_phase1 import MessageQueue
    
    llm = LLMWrapper(model='fast')
    queue = MessageQueue()
    
    # Create evaluator agent
    evaluator = EvaluatorAgent(queue, llm)
    
    print(f"✅ {evaluator.name} initialized")
    print(f"   Role: {evaluator.role}")
    print()
    

     # Mock analysis from analyst
    mock_analysis = {
        'title': 'Attention Is All You Need',
        'authors': ['Vaswani et al.'],
        'key_contributions': [
            'Introduced Transformer architecture',
            'Replaced RNNs with self-attention',
            'Achieved state-of-the-art on translation'
        ],
        'methodology': {
            'approach': 'Transformer neural network with multi-head attention',
            'datasets': ['WMT 2014 English-German', 'WMT 2014 English-French'],
            'evaluation_metrics': ['BLEU score', 'Training time']
        },
        'main_results': {
            'summary': 'Best BLEU score on translation tasks',
            'performance_improvements': [
                '28.4 BLEU on WMT 2014 English-German',
                'Trained in fraction of time vs RNN models'
            ]
        },
        'limitations': [
            'Memory intensive for very long sequences',
            'Less interpretable than RNNs'
        ],
        'novelty_assessment': {
            'score': 9,
            'reasoning': 'Revolutionary architecture that changed NLP'
        }
    }

     # Create test message
    test_message = Message(
        sender="analyst",
        recipient="evaluator",
        message_type=MessageType.REQUEST,
        content={
            'action': 'evaluate',
            'analysis': mock_analysis
        }
    )
    
    # Process
    print("🧪 Testing with mock Transformer paper analysis...")
    print()
    
    result = evaluator.process(test_message)
    
    print("\n" + "="*60)
    print("⚖️ EVALUATION RESULT")
    print("="*60)
    
    # Show summary
    if 'error' not in result:
        summary = evaluator.generate_review_summary(result)
        print(summary)
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n" + "="*60)
    print("📋 FULL EVALUATION (JSON)")
    print("="*60)
    print(json.dumps(result, indent=2))
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo_evaluator()