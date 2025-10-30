"""
demo_phase2.py
Phase 2 Complete Integration Demo
Analyst + Evaluator agents working together
"""


import sys
import time
import json
from pathlib import Path


# Import Phase 1 components
from demo_phase1 import (
    MultiAgentSystem, Message, MessageType, Priority
)


# FIXED: Import Phase 2 components from packages
from tools.llm_wrapper import LLMWrapper
from tools.pdf_reader import PDFReader
from agents.analyst_agent import AnalystAgent
from agents.evaluator_agent import EvaluatorAgent


class Phase2System(MultiAgentSystem):
    """
    Extended system with Analyst and Evaluator agents
    """
    
    def __init__(self, groq_api_key=None):
        super().__init__()
        
        print("🔧 Initializing Phase 2 components...")
        
         # Initialize tools
        self.llm = LLMWrapper(api_key=groq_api_key, model='fast')
        self.pdf_reader = PDFReader()

         # Create and register Analyst agent
        self.analyst = AnalystAgent(
            message_queue=self.message_queue,
            llm=self.llm,
            pdf_reader=self.pdf_reader
        )
        self.register_agent(self.analyst)
        
        # Create and register Evaluator agent
        self.evaluator = EvaluatorAgent(
            message_queue=self.message_queue,
            llm=self.llm
        )
        self.register_agent(self.evaluator)
        
        print("✅ Phase 2 system ready!")
        print(f"   Agents: {len(self.agents)}")
        print(f"   - Supervisor")
        print(f"   - Analyst")
        print(f"   - Evaluator")
        print()
    
    def analyze_paper(self, paper_path: str) -> dict:
        """
        Complete paper analysis workflow
        
        Steps:
        1. Validate PDF
        2. Analyst extracts information
        3. Evaluator assesses quality
        4. Supervisor aggregates results
        
        Returns:
        {
            'analysis': {...},
            'evaluation': {...},
            'summary': {...}
        }
        """
        print("="*60)
        print("📄 ANALYZING RESEARCH PAPER")
        print("="*60)
        print(f"Paper: {paper_path}")
        print()

        # Step 1: Validate PDF
        print("🔍 Step 1: Validating PDF...")
        validation = self.pdf_reader.validate_pdf(paper_path)
        
        if not validation['valid']:
            print(f"❌ PDF validation failed: {validation['errors']}")
            return {'error': 'Invalid PDF', 'details': validation}
        
        print(f"✅ PDF valid ({validation['num_pages']} pages)")
        print()    
     
         # Step 2: Send to Analyst
        print("🔬 Step 2: Sending to Analyst agent...")
        
        analyst_message = Message(
            sender="user",
            recipient="analyst",
            message_type=MessageType.REQUEST,
            content={
                'action': 'analyze',
                'paper_path': paper_path
            },
            priority=Priority.HIGH,
            requires_response=True
        )
        
        self.message_queue.send(analyst_message)

         # Wait for analyst response
        print("⏳ Waiting for analyst...")
        analysis_result = None
        
        for _ in range(30):  # Wait up to 30 seconds
            response = self.message_queue.receive("user", timeout=1)
            
            if response and response.sender == "analyst":
                analysis_result = response.content.get('response', {})
                break
            
            time.sleep(1)
        
        if not analysis_result:
            print("❌ Analyst timed out")
            return {'error': 'Analyst timeout'}
        
        if 'error' in analysis_result:
            print(f"❌ Analyst error: {analysis_result['error']}")
            return {'error': 'Analysis failed', 'details': analysis_result}
        
        print("✅ Analysis complete!")
        print(f"   Title: {analysis_result.get('title', 'N/A')}")
        print(f"   Novelty: {analysis_result.get('novelty_assessment', {}).get('score', 0)}/10")
        print()

    

          # Step 3: Send to Evaluator
        print("⚖️  Step 3: Sending to Evaluator agent...")
        
        evaluator_message = Message(
            sender="user",
            recipient="evaluator",
            message_type=MessageType.REQUEST,
            content={
                'action': 'evaluate',
                'analysis': analysis_result
            },
            priority=Priority.HIGH,
            requires_response=True
        )
        
        self.message_queue.send(evaluator_message)
        
        # Wait for evaluator response
        print("⏳ Waiting for evaluator...")
        evaluation_result = None

        for _ in range(30):
            response = self.message_queue.receive("user", timeout=1)
            
            if response and response.sender == "evaluator":
                evaluation_result = response.content.get('response', {})
                break
            
            time.sleep(1)
        
        if not evaluation_result:
            print("❌ Evaluator timed out")
            return {
                'analysis': analysis_result,
                'error': 'Evaluator timeout'
            }
        
        if 'error' in evaluation_result:
            print(f"❌ Evaluator error: {evaluation_result['error']}")
            return {
                'analysis': analysis_result,
                'error': 'Evaluation failed',
                'details': evaluation_result
            }
        
        print("✅ Evaluation complete!")
        print(f"   Overall Score: {evaluation_result.get('scores', {}).get('overall', 0)}/10")
        print(f"   Funding Potential: {evaluation_result.get('funding_potential', 'N/A')}")
        print()
        

         # Step 4: Create summary
        print("📊 Step 4: Creating summary...")
        
        summary = self._create_summary(analysis_result, evaluation_result)
        
        print("✅ Summary created!")
        print()
        
        return {
            'analysis': analysis_result,
            'evaluation': evaluation_result,
            'summary': summary,
            'pdf_info': validation
        }
    

    
    def _create_summary(self, analysis: dict, evaluation: dict) -> dict:
        """Create executive summary of results"""
        
        scores = evaluation.get('scores', {})
        
        summary = {
            'paper_title': analysis.get('title', 'Unknown'),
            'authors': analysis.get('authors', []),
            'overall_assessment': {
                'quality_score': scores.get('overall', 0),
                'novelty_score': analysis.get('novelty_assessment', {}).get('score', 0),
                'funding_potential': evaluation.get('funding_potential', 'UNKNOWN')
            },
            'key_strengths': evaluation.get('strengths', [])[:3],
            'key_weaknesses': evaluation.get('weaknesses', [])[:3],
            'main_contributions': analysis.get('key_contributions', [])[:3],
            'recommendation': self._generate_recommendation(analysis, evaluation)
        }
        
        return summary
    
    def _generate_recommendation(self, analysis: dict, evaluation: dict) -> str:
        """Generate final recommendation"""
        
        overall_score = evaluation.get('scores', {}).get('overall', 0)
        funding = evaluation.get('funding_potential', 'UNKNOWN')
        
        if overall_score >= 8 and funding == 'HIGH':
            return "STRONGLY RECOMMEND - High quality work with strong funding potential"
        elif overall_score >= 7 and funding in ['HIGH', 'MEDIUM']:
            return "RECOMMEND - Solid work, likely fundable with minor improvements"
        elif overall_score >= 6:
            return "CONDITIONAL - Promising work but needs significant improvements"
        elif overall_score >= 4:
            return "MAJOR REVISIONS - Core ideas good but execution needs work"
        else:
            return "NOT RECOMMENDED - Significant issues need to be addressed"
        

# ==================== DEMOS ====================

def demo_simple_analysis():
    """Simple demo with single paper"""
    
    print("="*60)
    print("🤖 PHASE 2 DEMO - SINGLE PAPER ANALYSIS")
    print("="*60)
    print()
    
    # Initialize system
    system = Phase2System()
    
    # Start agents
    system.start_all_agents()
    time.sleep(2)
    
    # Get paper path
    print("Enter path to PDF research paper:")
    paper_path = input("Path: ").strip()
    
    if not paper_path:
        print("⏭️  No path provided, using mock data...")
        demo_mock_analysis()
        return
    
    print()
    

    # Analyze
    result = system.analyze_paper(paper_path)
    
    # Display results
    print("\n" + "="*60)
    print("📊 ANALYSIS RESULTS")
    print("="*60)
    
    if 'error' in result:
        print(f"\n❌ Error: {result['error']}")
        if 'details' in result:
            print(f"Details: {result['details']}")
    else:
        # Show summary
        summary = result['summary']
        
        print(f"\n📄 Paper: {summary['paper_title']}")
        print(f"👥 Authors: {', '.join(summary['authors'][:3])}")
        
        print(f"\n📊 Assessment:")
        print(f"   Quality Score: {summary['overall_assessment']['quality_score']}/10")
        print(f"   Novelty Score: {summary['overall_assessment']['novelty_score']}/10")
        print(f"   Funding: {summary['overall_assessment']['funding_potential']}")
        
        print(f"\n✅ Strengths:")
        for i, strength in enumerate(summary['key_strengths'], 1):
            print(f"   {i}. {strength}")
        
        print(f"\n⚠️  Weaknesses:")
        for i, weakness in enumerate(summary['key_weaknesses'], 1):
            print(f"   {i}. {weakness}")
        
        print(f"\n🎯 Recommendation:")
        print(f"   {summary['recommendation']}")
        
        # Option to save
        print("\n" + "="*60)
        save = input("Save full results to JSON? (y/n): ").strip().lower()
        
        if save == 'y':
            output_path = "paper_analysis_result.json"
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ Saved to {output_path}")
    
    # Stop system
    print("\n🛑 Stopping system...")
    system.stop_all_agents()
    time.sleep(1)
    
    print("✅ Demo complete!")

def demo_mock_analysis():
    """Demo with mock data (no PDF required)"""
    
    print("="*60)
    print("🎭 MOCK ANALYSIS DEMO (No PDF required)")
    print("="*60)
    print()
    
    # Initialize system
    system = Phase2System()
    system.start_all_agents()
    time.sleep(2)
    
    # Create mock analysis
    print("Creating mock paper analysis...")

    mock_analysis = {
        'title': 'Attention Is All You Need',
        'authors': ['Vaswani', 'Shazeer', 'Parmar', 'et al.'],
        'year': 2017,
        'venue': 'NeurIPS 2017',
        'key_contributions': [
            'Introduced Transformer architecture using self-attention',
            'Eliminated recurrence in sequence modeling',
            'Achieved state-of-the-art translation performance',
            'Enabled massive parallelization during training'
        ],
        'methodology': {
            'approach': 'Multi-head self-attention with positional encodings',
            'datasets': ['WMT 2014 English-German', 'WMT 2014 English-French'],
            'evaluation_metrics': ['BLEU score', 'Training time']
        },
        'main_results': {
            'summary': 'Outperformed all previous models on translation tasks',
            'performance_improvements': [
                '28.4 BLEU on EN-DE (2.0 BLEU better than previous SOTA)',
                '41.8 BLEU on EN-FR (new state-of-the-art)',
                'Trained in 3.5 days vs weeks for RNN models'
            ]
        },
        'limitations': [
            'Memory complexity O(n²) for sequence length n',
            'Requires large datasets to train effectively',
            'Less interpretable attention patterns than expected'
        ],
        'novelty_assessment': {
            'score': 10,
            'reasoning': 'Revolutionary architecture that fundamentally changed NLP'
        },
        'gaps_identified': [
            'Efficiency for very long sequences',
            'Better understanding of attention mechanisms',
            'Applications beyond NLP'
        ]
    }
    
    # Send to evaluator
    print("📤 Sending to Evaluator...")
    
    eval_msg = Message(
        sender="demo",
        recipient="evaluator",
        message_type=MessageType.REQUEST,
        content={
            'action': 'evaluate',
            'analysis': mock_analysis
        },
        priority=Priority.HIGH,
        requires_response=True
    )
    
    system.message_queue.send(eval_msg)
    
    # Wait for response
    print("⏳ Waiting for evaluation...")
    
    evaluation = None
    for _ in range(30):
        response = system.message_queue.receive("demo", timeout=1)
        if response and response.sender == "evaluator":
            evaluation = response.content.get('response', {})
            break
        time.sleep(1)
    
    if not evaluation:
        print("❌ Evaluation timed out")
        system.stop_all_agents()
        return
    
    # Display results
    print("\n" + "="*60)
    print("📊 EVALUATION RESULTS")
    print("="*60)
    
    print(f"\n📄 Paper: {mock_analysis['title']}")
    print(f"👥 Authors: {', '.join(mock_analysis['authors'])}")
    print(f"📅 Year: {mock_analysis['year']}")
    print(f"📍 Venue: {mock_analysis['venue']}")
    
    print(f"\n📊 Scores:")
    for metric, score in evaluation.get('scores', {}).items():
        print(f"   {metric.capitalize()}: {score}/10")
    
    print(f"\n💰 Funding Potential: {evaluation.get('funding_potential', 'N/A')}")
    
    print(f"\n✅ Strengths:")
    for i, strength in enumerate(evaluation.get('strengths', []), 1):
        print(f"   {i}. {strength}")
    
    print(f"\n⚠️  Weaknesses:")
    for i, weakness in enumerate(evaluation.get('weaknesses', []), 1):
        print(f"   {i}. {weakness}")
    
    print(f"\n📝 Reviewer Feedback:")
    for i, feedback in enumerate(evaluation.get('reviewer_feedback', []), 1):
        print(f"   {i}. {feedback}")
    
    # Stop system
    print("\n🛑 Stopping system...")
    system.stop_all_agents()
    time.sleep(1)
    
    print("\n✅ Demo complete!")


def demo_system_status():
    """Show live system status"""
    
    print("="*60)
    print("📊 PHASE 2 SYSTEM STATUS")
    print("="*60)
    print()
    
    system = Phase2System()
    system.start_all_agents()
    time.sleep(2)
    
    # Show status
    status = system.get_system_status()
    
    print("Agent Status:")
    print("-" * 60)
    for name, agent_status in status['agents'].items():
        print(f"\n{name}:")
        for key, value in agent_status.items():
            print(f"  {key}: {value}")
    
    print("\n" + "-" * 60)
    print(f"Total Agents: {len(status['agents'])}")
    print(f"Message Queue: {status['message_queue_size']} pending")
    print(f"Active Tasks: {status['active_tasks']}")
    print(f"Completed Tasks: {status['completed_tasks']}")
    
    # LLM stats
    print("\n" + "="*60)
    print("🤖 LLM Statistics")
    print("="*60)
    llm_stats = system.llm.get_stats()
    for key, value in llm_stats.items():
        print(f"{key}: {value}")
    
    # Stop
    system.stop_all_agents()
    print("\n✅ Status check complete!")


# ==================== MAIN MENU ====================

def main_menu():
    """Main menu for Phase 2 demos"""
    
    print("="*60)
    print("🤖 MULTI-AGENT SYSTEM - PHASE 2 DEMOS")
    print("="*60)
    print()
    print("Choose a demo:")
    print()
    print("  1. Analyze PDF Paper     - Full analysis workflow")
    print("  2. Mock Analysis Demo    - Test without PDF")
    print("  3. System Status         - Check agent status")
    print("  4. Interactive Mode      - Manual agent testing")
    print("  5. Exit")
    print()
    
    while True:
        choice = input("Enter choice (1-5): ").strip()
        print()
        
        if choice == '1':
            demo_simple_analysis()
            break
        
        elif choice == '2':
            demo_mock_analysis()
            break
        
        elif choice == '3':
            demo_system_status()
            break
        
        elif choice == '4':
            print("🚧 Interactive mode - Coming in Phase 3!")
            break
        
        elif choice == '5':
            print("Goodbye! 👋")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-5.")
            print()


if __name__ == "__main__":
    main_menu()