"""
demo_phase3.py
Phase 3 Complete Integration
All 5 agents working together with conflict resolution
"""


import sys
import time
import json
from pathlib import Path


# Import Phase 1 & 2 components
from demo_phase1 import (
    MultiAgentSystem, Message, MessageType, Priority
)
from tools.llm_wrapper import LLMWrapper
from tools.pdf_reader import PDFReader
from agents.analyst_agent import AnalystAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.innovator_agent import InnovatorAgent
from agents.writer_agent import WriterAgent


class Phase3System(MultiAgentSystem):
    """
    Complete system with all 5 agents:
    1. Supervisor - Orchestrates workflow
    2. Analyst - Extracts information
    3. Evaluator - Assesses quality
    4. Innovator - Generates future directions
    5. Writer - Creates grant proposal
    """

    def __init__(self, groq_api_key=None):
        super().__init__()
        
        print("🔧 Initializing Phase 3 - Complete System...")
        
        # Initialize tools
        self.llm = LLMWrapper(api_key=groq_api_key, model='fast')
        self.pdf_reader = PDFReader()
        
        # Create and register all agents
        self.analyst = AnalystAgent(
            message_queue=self.message_queue,
            llm=self.llm,
            pdf_reader=self.pdf_reader
        )
        self.register_agent(self.analyst)
        
        self.evaluator = EvaluatorAgent(
            message_queue=self.message_queue,
            llm=self.llm
        )
        self.register_agent(self.evaluator)
        
        self.innovator = InnovatorAgent(
            message_queue=self.message_queue,
            llm=self.llm
        )
        self.register_agent(self.innovator)
        
        self.writer = WriterAgent(
            message_queue=self.message_queue,
            llm=self.llm
        )
        self.register_agent(self.writer)
        
        print("✅ Phase 3 system ready!")
        print(f"   Total Agents: {len(self.agents)}")
        print(f"   - Supervisor (Orchestrator)")
        print(f"   - Analyst (Paper Analysis)")
        print(f"   - Evaluator (Quality Assessment)")
        print(f"   - Innovator (Future Directions)")
        print(f"   - Writer (Grant Proposal)")
        print()

    def generate_grant_proposal(self, paper_path: str) -> dict:
        """
        Complete end-to-end workflow:
        Paper PDF → Grant Proposal
        
        Steps:
        1. Validate PDF
        2. Analyst extracts information
        3. Evaluator assesses quality
        4. Innovator generates future directions
        5. Detect conflicts between agents
        6. Writer synthesizes into grant proposal
        
        Returns complete grant proposal
        """
        print("="*70)
        print("📄 GENERATING GRANT PROPOSAL")
        print("="*70)
        print(f"Paper: {paper_path}")
        print()

          # Step 1: Validate PDF
        print("🔍 Step 1/5: Validating PDF...")
        validation = self.pdf_reader.validate_pdf(paper_path)
        
        if not validation['valid']:
            print(f"❌ PDF validation failed: {validation['errors']}")
            return {'error': 'Invalid PDF', 'details': validation}
        
        print(f"✅ PDF valid ({validation['num_pages']} pages)")
        print()

         # Step 2: Analyst Analysis
        print("🔬 Step 2/5: Analyst extracting information...")
        analysis_result = self._get_analysis(paper_path)
        
        if 'error' in analysis_result:
            print(f"❌ Analysis failed: {analysis_result['error']}")
            return {'error': 'Analysis failed', 'details': analysis_result}
        
        print("✅ Analysis complete!")
        print(f"   Title: {analysis_result.get('title', 'N/A')}")
        print(f"   Novelty: {analysis_result.get('novelty_assessment', {}).get('score', 0)}/10")
        print()


        # Step 3: Evaluator Assessment
        print("⚖️  Step 3/5: Evaluator assessing quality...")
        evaluation_result = self._get_evaluation(analysis_result)
        
        if 'error' in evaluation_result:
            print(f"❌ Evaluation failed: {evaluation_result['error']}")
            return {
                'analysis': analysis_result,
                'error': 'Evaluation failed',
                'details': evaluation_result
            }
        
        print("✅ Evaluation complete!")
        print(f"   Overall Score: {evaluation_result.get('scores', {}).get('overall', 0)}/10")
        print(f"   Funding Potential: {evaluation_result.get('funding_potential', 'N/A')}")
        print()   


         # Step 4: Innovator Future Directions
        print("💡 Step 4/5: Innovator generating future directions...")
        innovation_result = self._get_innovations(analysis_result, evaluation_result)
        
        if 'error' in innovation_result:
            print(f"❌ Innovation failed: {innovation_result['error']}")
            return {
                'analysis': analysis_result,
                'evaluation': evaluation_result,
                'error': 'Innovation failed',
                'details': innovation_result
            }
        
        print("✅ Innovation complete!")
        print(f"   Future Directions: {len(innovation_result.get('future_directions', []))}")
        print(f"   Commercial Potential: {innovation_result.get('commercial_potential', 'N/A')}")
        print() 


         # Step 4.5: Detect Conflicts
        print("🔍 Detecting conflicts between agents...")
        conflicts = self._detect_conflicts(analysis_result, evaluation_result, innovation_result)
        
        if conflicts:
            print(f"⚠️  Found {len(conflicts)} conflict(s):")
            for conflict in conflicts:
                print(f"   - {conflict['type']}: {conflict['description']}")
        else:
            print("✅ No conflicts detected")
        print()
        
         # Step 5: Writer Synthesis
        print("✍️  Step 5/5: Writer synthesizing grant proposal...")
        proposal_result = self._get_proposal(
            analysis_result,
            evaluation_result,
            innovation_result,
            conflicts
        )
        
        if 'error' in proposal_result:
            print(f"❌ Proposal generation failed: {proposal_result['error']}")
            return {
                'analysis': analysis_result,
                'evaluation': evaluation_result,
                'innovations': innovation_result,
                'error': 'Proposal failed',
                'details': proposal_result
            }
        
        word_count = proposal_result.get('word_count', 0)
        print(f"✅ Proposal complete! ({word_count} words)")
        print()
        
        # Return complete result
        return {
            'analysis': analysis_result,
            'evaluation': evaluation_result,
            'innovations': innovation_result,
            'conflicts': conflicts,
            'proposal': proposal_result,
            'pdf_info': validation,
            'success': True
        }
    
    def _get_analysis(self, paper_path: str) -> dict:
        """Get analysis from Analyst agent"""
        
        msg = Message(
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
        
        self.message_queue.send(msg)
        
        # Wait for response
        for _ in range(30):
            response = self.message_queue.receive("user", timeout=1)
            if response and response.sender == "analyst":
                return response.content.get('response', {})
            time.sleep(1)
        
        return {'error': 'Analyst timeout'}
    
    def _get_evaluation(self, analysis: dict) -> dict:
        """Get evaluation from Evaluator agent"""
        
        msg = Message(
            sender="user",
            recipient="evaluator",
            message_type=MessageType.REQUEST,
            content={
                'action': 'evaluate',
                'analysis': analysis
            },
            priority=Priority.HIGH,
            requires_response=True
        )
        
        self.message_queue.send(msg)
        
        # Wait for response
        for _ in range(30):
            response = self.message_queue.receive("user", timeout=1)
            if response and response.sender == "evaluator":
                return response.content.get('response', {})
            time.sleep(1)
        
        return {'error': 'Evaluator timeout'}
    
    def _get_innovations(self, analysis: dict, evaluation: dict) -> dict:
        """Get innovations from Innovator agent"""
        
        msg = Message(
            sender="user",
            recipient="innovator",
            message_type=MessageType.REQUEST,
            content={
                'action': 'innovate',
                'analysis': analysis,
                'evaluation': evaluation
            },
            priority=Priority.HIGH,
            requires_response=True
        )
        
        self.message_queue.send(msg)
        
        # Wait for response
        for _ in range(30):
            response = self.message_queue.receive("user", timeout=1)
            if response and response.sender == "innovator":
                return response.content.get('response', {})
            time.sleep(1)
        
        return {'error': 'Innovator timeout'}
    def _get_proposal(
        self,
        analysis: dict,
        evaluation: dict,
        innovations: dict,
        conflicts: list
    ) -> dict:
        """Get proposal from Writer agent"""
        
        msg = Message(
            sender="user",
            recipient="writer",
            message_type=MessageType.REQUEST,
            content={
                'action': 'write_proposal',
                'analysis': analysis,
                'evaluation': evaluation,
                'innovations': innovations,
                'conflicts': conflicts
            },
            priority=Priority.HIGH,
            requires_response=True
        )
        
        self.message_queue.send(msg)

         # Wait for response
        for _ in range(45):  # Longer timeout for writing
            response = self.message_queue.receive("user", timeout=1)
            if response and response.sender == "writer":
                return response.content.get('response', {})
            time.sleep(1)
        
        return {'error': 'Writer timeout'}
    
    def _detect_conflicts(
        self,
        analysis: dict,
        evaluation: dict,
        innovations: dict
    ) -> list:
        """Detect conflicts between agent assessments"""
        
        conflicts = []

         # Conflict 1: Novelty disagreement
        analyst_novelty = analysis.get('novelty_assessment', {}).get('score', 0)
        evaluator_originality = evaluation.get('scores', {}).get('originality', 0)
        
        if abs(analyst_novelty - evaluator_originality) >= 3:
            conflicts.append({
                'type': 'novelty_assessment',
                'description': f'Analyst rated novelty {analyst_novelty}/10, Evaluator rated originality {evaluator_originality}/10',
                'agents': ['analyst', 'evaluator'],
                'severity': 'HIGH' if abs(analyst_novelty - evaluator_originality) >= 5 else 'MEDIUM',
                'resolution': f'Weighted average: {(analyst_novelty + evaluator_originality) / 2:.1f}/10'
            })

         # Conflict 2: Funding potential disagreement
        evaluator_funding = evaluation.get('funding_potential', 'UNKNOWN')
        innovator_commercial = innovations.get('commercial_potential', 'UNKNOWN')
        
        funding_map = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'UNKNOWN': 0}
        eval_score = funding_map.get(evaluator_funding, 0)
        innov_score = funding_map.get(innovator_commercial, 0)

        if abs(eval_score - innov_score) >= 2:
            conflicts.append({
                'type': 'funding_potential',
                'description': f'Evaluator: {evaluator_funding}, Innovator: {innovator_commercial}',
                'agents': ['evaluator', 'innovator'],
                'severity': 'MEDIUM',
                'resolution': 'Consider evaluator assessment (quality-focused) with innovator vision (application-focused)'
            })
           
         
        # Conflict 3: Quality vs Innovation mismatch
        overall_quality = evaluation.get('scores', {}).get('overall', 0)
        breakthrough_score = innovations.get('breakthrough_potential', {}).get('score', 0)
        
        if overall_quality >= 8 and breakthrough_score <= 3:
            conflicts.append({
                'type': 'quality_innovation_mismatch',
                'description': f'High quality ({overall_quality}/10) but low breakthrough potential ({breakthrough_score}/10)',
                'agents': ['evaluator', 'innovator'],
                'severity': 'LOW',
                'resolution': 'High-quality incremental work - valuable but not transformative'
            })
        
        return conflicts
    
# ==================== DEMOS ====================

def demo_full_workflow():
    """Complete end-to-end demo"""
    
    print("="*70)
    print("🤖 PHASE 3 - COMPLETE GRANT PROPOSAL GENERATION")
    print("="*70)
    print()
    
    # Initialize system
    system = Phase3System()
    
    # Start all agents
    system.start_all_agents()
    time.sleep(2)
    
    # Get paper path
    print("Enter path to PDF research paper:")
    paper_path = input("Path: ").strip()
    
    if not paper_path:
        print("⏭️  No path provided, switching to mock demo...")
        system.stop_all_agents()
        time.sleep(1)
        demo_mock_workflow()
        return
    
    print()

     # Generate proposal
    result = system.generate_grant_proposal(paper_path)
    
    # Display results
    print("\n" + "="*70)
    print("📊 GRANT PROPOSAL RESULTS")
    print("="*70)
    
    if 'error' in result:
        print(f"\n❌ Error: {result['error']}")
        if 'details' in result:
            print(f"Details: {result['details']}")
    else:
        # Show summary
        print(f"\n📄 Paper: {result['analysis'].get('title', 'N/A')}")
        print(f"👥 Authors: {', '.join(result['analysis'].get('authors', [])[:3])}")
        
        print(f"\n📊 Assessment:")
        print(f"   Quality: {result['evaluation'].get('scores', {}).get('overall', 0)}/10")
        print(f"   Novelty: {result['analysis'].get('novelty_assessment', {}).get('score', 0)}/10")
        print(f"   Funding: {result['evaluation'].get('funding_potential', 'N/A')}")
        print(f"   Commercial: {result['innovations'].get('commercial_potential', 'N/A')}")
        
        if result.get('conflicts'):
            print(f"\n⚠️  Conflicts Resolved: {len(result['conflicts'])}")
            for conflict in result['conflicts']:
                print(f"   - {conflict['type']}: {conflict['resolution']}")
        
        print(f"\n📝 Proposal Generated:")
        print(f"   Word Count: {result['proposal'].get('word_count', 0)}")
        print(f"   Sections: {len(result['proposal'].get('proposal', {}))}")
        
         # Show preview
        print(f"\n📄 Proposal Preview (first 500 chars):")
        print("-" * 70)
        full_text = result['proposal'].get('full_text', '')
        print(full_text[:500])
        print("...\n")
        
        # Option to save
        print("="*70)
        save = input("Save complete results? (y/n): ").strip().lower()
        
        if save == 'y':
            # Save JSON
            with open('grant_proposal_data.json', 'w') as f:
                json.dump({
                    'analysis': result['analysis'],
                    'evaluation': result['evaluation'],
                    'innovations': result['innovations'],
                    'conflicts': result['conflicts'],
                    'metadata': result['proposal']['metadata']
                }, f, indent=2)
            
            # Save full proposal
            with open('grant_proposal.txt', 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            print("✅ Saved:")
            print("   - grant_proposal_data.json (structured data)")
            print("   - grant_proposal.txt (full proposal)")
 # Stop system
    print("\n🛑 Stopping system...")
    system.stop_all_agents()
    time.sleep(1)
    
    print("✅ Demo complete!")


def demo_mock_workflow():
    """Demo with mock data (no PDF required)"""
    
    print("="*70)
    print("🎭 MOCK WORKFLOW DEMO (No PDF required)")
    print("="*70)
    print()
    
    # Initialize system
    system = Phase3System()
    system.start_all_agents()
    time.sleep(2)
    
    print("Using mock data from 'Attention Is All You Need' paper...")
    print()
    
     # Mock analysis
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
            'summary': 'Outperformed all previous models',
            'performance_improvements': [
                '28.4 BLEU on EN-DE',
                'Trained in 3.5 days vs weeks'
            ]
        },
        'limitations': [
            'Memory complexity O(n²)',
            'Requires large datasets'
        ],
        'novelty_assessment': {
            'score': 10,
            'reasoning': 'Revolutionary architecture'
        },
        'gaps_identified': [
            'Efficiency for long sequences',
            'Applications beyond NLP'
        ]
    }

     # Get evaluation
    print("⚖️  Step 1/3: Getting evaluation...")
    eval_msg = Message(
        sender="demo",
        recipient="evaluator",
        message_type=MessageType.REQUEST,
        content={'action': 'evaluate', 'analysis': mock_analysis},
        priority=Priority.HIGH,
        requires_response=True
    )
    system.message_queue.send(eval_msg)
    
    evaluation = None
    for _ in range(30):
        resp = system.message_queue.receive("demo", timeout=1)
        if resp and resp.sender == "evaluator":
            evaluation = resp.content.get('response', {})
            break
        time.sleep(1)
    
    if not evaluation:
        print("❌ Evaluation timeout")
        system.stop_all_agents()
        return
    
    print("✅ Evaluation complete!")
    print()

    # Get innovations
    print("💡 Step 2/3: Getting innovations...")
    innov_msg = Message(
        sender="demo",
        recipient="innovator",
        message_type=MessageType.REQUEST,
        content={'action': 'innovate', 'analysis': mock_analysis, 'evaluation': evaluation},
        priority=Priority.HIGH,
        requires_response=True
    )
    system.message_queue.send(innov_msg)
    
    innovations = None
    for _ in range(30):
        resp = system.message_queue.receive("demo", timeout=1)
        if resp and resp.sender == "innovator":
            innovations = resp.content.get('response', {})
            break
        time.sleep(1)
    
    if not innovations:
        print("❌ Innovation timeout")
        system.stop_all_agents()
        return
    
    print("✅ Innovation complete!")
    print()


     # Detect conflicts
    conflicts = system._detect_conflicts(mock_analysis, evaluation, innovations)
    
    # Get proposal
    print("✍️  Step 3/3: Generating proposal...")
    writer_msg = Message(
        sender="demo",
        recipient="writer",
        message_type=MessageType.REQUEST,
        content={
            'action': 'write_proposal',
            'analysis': mock_analysis,
            'evaluation': evaluation,
            'innovations': innovations,
            'conflicts': conflicts
        },
        priority=Priority.HIGH,
        requires_response=True
    )
    system.message_queue.send(writer_msg)
    
    proposal = None
    for _ in range(45):
        resp = system.message_queue.receive("demo", timeout=1)
        if resp and resp.sender == "writer":
            proposal = resp.content.get('response', {})
            break
        time.sleep(1)
    
    if not proposal:
        print("❌ Proposal timeout")
        system.stop_all_agents()
        return
    
    print("✅ Proposal complete!")
    print()
    
    # Display results
    print("="*70)
    print("📊 RESULTS")
    print("="*70)
    
    print(f"\n📊 Scores:")
    for metric, score in evaluation.get('scores', {}).items():
        print(f"   {metric.capitalize()}: {score}/10")
    
    print(f"\n💡 Future Directions: {len(innovations.get('future_directions', []))}")
    for i, direction in enumerate(innovations.get('future_directions', [])[:3], 1):
        print(f"   {i}. {direction.get('direction', 'N/A')}")
    
    if conflicts:
        print(f"\n⚠️  Conflicts: {len(conflicts)}")
        for conflict in conflicts:
            print(f"   - {conflict['type']}")
    
    print(f"\n📝 Proposal:")
    print(f"   Words: {proposal.get('word_count', 0)}")
    print(f"   Sections: {len(proposal.get('proposal', {}))}")
    
    # Save option
    save = input("\nSave proposal? (y/n): ").strip().lower()
    if save == 'y':
        with open('mock_grant_proposal.txt', 'w', encoding='utf-8') as f:
            f.write(proposal.get('full_text', ''))
        print("✅ Saved to mock_grant_proposal.txt")
    
    # Stop
    system.stop_all_agents()
    print("\n✅ Demo complete!")


# ==================== MAIN MENU ====================

def main_menu():
    """Main menu for Phase 3 demos"""
    
    print("="*70)
    print("🤖 MULTI-AGENT SYSTEM - PHASE 3 COMPLETE")
    print("="*70)
    print()
    print("Choose a demo:")
    print()
    print("  1. Full Workflow          - Analyze PDF → Generate Grant Proposal")
    print("  2. Mock Workflow          - Test without PDF")
    print("  3. System Status          - Check all agents")
    print("  4. Exit")
    print()
    
    while True:
        choice = input("Enter choice (1-4): ").strip()
        print()
        
        if choice == '1':
            demo_full_workflow()
            break
        
        elif choice == '2':
            demo_mock_workflow()
            break
        
        elif choice == '3':
            system = Phase3System()
            system.start_all_agents()
            time.sleep(2)
            status = system.get_system_status()
            print(json.dumps(status, indent=2))
            system.stop_all_agents()
            break
        
        elif choice == '4':
            print("Goodbye! 👋")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-4.")
            print()


if __name__ == "__main__":
    main_menu()