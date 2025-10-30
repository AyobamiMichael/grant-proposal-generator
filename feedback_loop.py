"""
feedback_loop.py
Interactive feedback and refinement system
"""

import json
from typing import Dict, List
from datetime import datetime

from tools.llm_wrapper import LLMWrapper


class FeedbackSystem:
    """
    Human-in-the-loop feedback system
    
    Features:
    - Interactive proposal review
    - Section-by-section feedback
    - Automated refinement based on feedback
    - Version history tracking
    - Collaborative editing
    """
    
    def __init__(self, llm: LLMWrapper = None):
        self.llm = llm or LLMWrapper(model='fast')
        self.versions = []
        self.feedback_history = []
    

    def collect_feedback(
        self,
        proposal_data: Dict,
        interactive: bool = True
    ) -> Dict:
        """
        Collect feedback on proposal
        
        Args:
            proposal_data: Complete proposal from Phase 3
            interactive: Use interactive CLI (vs structured input)
        
        Returns:
            Structured feedback dictionary
        """
        print("="*70)
        print("💬 FEEDBACK COLLECTION")
        print("="*70)
        print()

        if interactive:
            return self._collect_interactive_feedback(proposal_data)
        else:
            return self._collect_structured_feedback(proposal_data)
    
    
    def _collect_interactive_feedback(self, proposal_data: Dict) -> Dict:
        """Interactive CLI feedback collection"""
        
        proposal = proposal_data.get('proposal', {}).get('proposal', {})
        
        print("Review each section and provide feedback:")
        print("  - Type 'good' if section is acceptable")
        print("  - Type specific feedback for improvements")
        print("  - Type 'skip' to skip section")
        print()
        
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'sections': {},
            'general_comments': ''
        }
        
        # Review each section
        sections_to_review = [
            'executive_summary',
            'project_description',
            'research_plan',
            'broader_impacts',
            'budget_justification'
        ]
        
        for section_name in sections_to_review:
            if section_name not in proposal:
                continue
            
            print("\n" + "="*70)
            print(f"📄 SECTION: {section_name.replace('_', ' ').upper()}")
            print("="*70)
            
            # Show preview
            content = proposal[section_name]
            preview = str(content)[:500] + "..." if len(str(content)) > 500 else str(content)
            print(f"\n{preview}\n")
            
            print("-"*70)
            user_feedback = input(f"Feedback for {section_name} (or 'good'/'skip'): ").strip()
            
            if user_feedback.lower() == 'skip':
                continue
            elif user_feedback.lower() == 'good':
                feedback['sections'][section_name] = {
                    'status': 'approved',
                    'comments': 'Section approved'
                }
            else:
                feedback['sections'][section_name] = {
                    'status': 'needs_revision',
                    'comments': user_feedback
                }
        
        # General feedback
        print("\n" + "="*70)
        print("💭 GENERAL FEEDBACK")
        print("="*70)
        general = input("Any general comments on the proposal? (press Enter to skip): ").strip()
        if general:
            feedback['general_comments'] = general
        
        # Overall assessment
        print("\n" + "="*70)
        print("⭐ OVERALL ASSESSMENT")
        print("="*70)
        
        while True:
            rating = input("Overall rating (1-5 stars): ").strip()
            try:
                rating_int = int(rating)
                if 1 <= rating_int <= 5:
                    feedback['overall_rating'] = rating_int
                    break
                else:
                    print("Please enter a number between 1 and 5")
            except ValueError:
                print("Please enter a valid number")
        
        # Save feedback
        self.feedback_history.append(feedback)
        
        return feedback
    
    def _collect_structured_feedback(self, proposal_data: Dict) -> Dict:
        """Collect feedback via structured format"""
        
        # This would be used with a web UI or API
        feedback_template = {
            'timestamp': datetime.now().isoformat(),
            'sections': {},
            'general_comments': '',
            'overall_rating': 0
        }
        
        print("Use this template for structured feedback:")
        print(json.dumps(feedback_template, indent=2))
        
        return feedback_template
    
    def refine_proposal(
        self,
        proposal_data: Dict,
        feedback: Dict
    ) -> Dict:
        """
        Refine proposal based on feedback
        
        Args:
            proposal_data: Original proposal
            feedback: Feedback dictionary
        
        Returns:
            Refined proposal data
        """
        print("\n" + "="*70)
        print("✨ REFINING PROPOSAL BASED ON FEEDBACK")
        print("="*70)
        print()
        
        # Save current version
        self.versions.append({
            'version': len(self.versions) + 1,
            'timestamp': datetime.now().isoformat(),
            'data': proposal_data.copy()
        })
        
        # Refine sections that need revision
        refined_proposal = proposal_data.copy()
        proposal_sections = refined_proposal.get('proposal', {}).get('proposal', {})
        
        sections_to_refine = [
            section for section, details in feedback.get('sections', {}).items()
            if details.get('status') == 'needs_revision'
        ]
        
        if not sections_to_refine:
            print("✅ No sections need revision!")
            return refined_proposal
        
        print(f"Refining {len(sections_to_refine)} section(s)...")
        print()
        
        for section_name in sections_to_refine:
            print(f"🔄 Refining: {section_name}")
            
            original_content = proposal_sections.get(section_name, '')
            section_feedback = feedback['sections'][section_name]['comments']
            
            # Use LLM to refine
            refined_content = self._refine_section(
                section_name=section_name,
                original_content=original_content,
                feedback=section_feedback,
                context=proposal_data
            )
            
            # Update proposal
            proposal_sections[section_name] = refined_content
            print(f"✅ {section_name} refined")
        
        print()
        print("="*70)
        print("✅ REFINEMENT COMPLETE")
        print("="*70)
        
        return refined_proposal
    
    def _refine_section(
        self,
        section_name: str,
        original_content: str,
        feedback: str,
        context: Dict
    ) -> str:
        """Refine a single section using LLM"""
        
        # Build refinement prompt
        prompt = f"""You are refining a grant proposal section based on reviewer feedback.

SECTION: {section_name.replace('_', ' ').upper()}

ORIGINAL CONTENT:
{original_content}

REVIEWER FEEDBACK:
{feedback}

CONTEXT:
- Paper: {context.get('analysis', {}).get('title', 'Unknown')}
- Quality Score: {context.get('evaluation', {}).get('scores', {}).get('overall', 'N/A')}/10
- Funding Potential: {context.get('evaluation', {}).get('funding_potential', 'N/A')}

INSTRUCTIONS:
1. Address all points in the feedback
2. Maintain professional grant writing style
3. Keep the same section structure
4. Preserve key information from original
5. Make specific, concrete improvements
6. Do NOT make the section significantly longer unless requested

Provide the refined section content:"""
        
        try:
            refined = self.llm.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.6
            )
            
            return refined.strip()
            
        except Exception as e:
            print(f"⚠️  Refinement error: {e}")
            print("   Keeping original content")
            return original_content
    
    
    def compare_versions(self, version1_idx: int, version2_idx: int):
        """Compare two versions of the proposal"""
        
        if version1_idx >= len(self.versions) or version2_idx >= len(self.versions):
            print("❌ Invalid version numbers")
            return
        
        v1 = self.versions[version1_idx]
        v2 = self.versions[version2_idx]
        
        print("="*70)
        print(f"📊 COMPARING VERSIONS {version1_idx + 1} vs {version2_idx + 1}")
        print("="*70)
        print()
        
        print(f"Version {version1_idx + 1}: {v1['timestamp']}")
        print(f"Version {version2_idx + 1}: {v2['timestamp']}")
        print()
        
        # Compare sections
        prop1 = v1['data'].get('proposal', {}).get('proposal', {})
        prop2 = v2['data'].get('proposal', {}).get('proposal', {})
        
        for section_name in prop1.keys():
            if section_name == 'timeline':
                continue
            
            content1 = str(prop1.get(section_name, ''))
            content2 = str(prop2.get(section_name, ''))
            
            if content1 != content2:
                print(f"📝 {section_name.upper()} - CHANGED")
                print(f"   Length: {len(content1)} → {len(content2)} chars")
                print()
    
    def generate_feedback_report(self, output_path: str = "feedback_report.txt"):
        """Generate a report of all feedback received"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("FEEDBACK HISTORY REPORT\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Total Feedback Rounds: {len(self.feedback_history)}\n")
            f.write(f"Total Versions: {len(self.versions)}\n\n")
            
            for i, feedback in enumerate(self.feedback_history, 1):
                f.write(f"\nROUND {i}\n")
                f.write("-"*70 + "\n")
                f.write(f"Timestamp: {feedback['timestamp']}\n")
                f.write(f"Overall Rating: {feedback.get('overall_rating', 'N/A')}/5\n\n")
                
                f.write("Section Feedback:\n")
                for section, details in feedback.get('sections', {}).items():
                    f.write(f"\n{section.upper()}:\n")
                    f.write(f"  Status: {details['status']}\n")
                    f.write(f"  Comments: {details['comments']}\n")
                
                if feedback.get('general_comments'):
                    f.write(f"\nGeneral Comments:\n{feedback['general_comments']}\n")
                
                f.write("\n" + "="*70 + "\n")
        
        print(f"✅ Feedback report saved: {output_path}")
    
    def export_version(self, version_idx: int, output_path: str):
        """Export a specific version"""
        
        if version_idx >= len(self.versions):
            print(f"❌ Version {version_idx + 1} does not exist")
            return
        
        version_data = self.versions[version_idx]['data']
        
        with open(output_path, 'w') as f:
            json.dump(version_data, f, indent=2)
        
        print(f"✅ Version {version_idx + 1} exported: {output_path}")
    


# ==================== INTERACTIVE SESSION ====================

class InteractiveFeedbackSession:
    """Interactive feedback session manager"""
    
    def __init__(self, proposal_data: Dict):
        self.proposal_data = proposal_data
        self.feedback_system = FeedbackSystem()
        self.current_version = proposal_data
    
    def run(self):
        """Run interactive feedback loop"""
        
        print("="*70)
        print("🔄 INTERACTIVE FEEDBACK SESSION")
        print("="*70)
        print()
        print("This session allows you to iteratively refine the proposal")
        print("through multiple rounds of feedback.")
        print()
        
        round_number = 1
        
        while True:
            print("\n" + "="*70)
            print(f"📍 ROUND {round_number}")
            print("="*70)
            print()
            
            print("Options:")
            print("  1. Review and provide feedback")
            print("  2. View current proposal")
            print("  3. View feedback history")
            print("  4. Compare versions")
            print("  5. Export current version")
            print("  6. Finish and save")
            print()
            

            choice = input("Choose an option (1-6): ").strip()
            
            if choice == '1':
                # Collect feedback
                feedback = self.feedback_system.collect_feedback(
                    self.current_version,
                    interactive=True
                )
                
                # Refine proposal
                if any(details.get('status') == 'needs_revision' 
                       for details in feedback.get('sections', {}).values()):
                    
                    refine = input("\nRefine proposal based on feedback? (y/n): ").strip().lower()
                    if refine == 'y':
                        self.current_version = self.feedback_system.refine_proposal(
                            self.current_version,
                            feedback
                        )
                        round_number += 1
                else:
                    print("\n✅ All sections approved!")
                    finish = input("Finish session? (y/n): ").strip().lower()
                    if finish == 'y':
                        break
            
            elif choice == '2':
                # View proposal
                proposal = self.current_version.get('proposal', {}).get('proposal', {})
                print("\n📄 CURRENT PROPOSAL SECTIONS:\n")
                for section_name in proposal.keys():
                    print(f"  - {section_name.replace('_', ' ').upper()}")
                
                section_to_view = input("\nEnter section name to view (or Enter to skip): ").strip()
                if section_to_view:
                    section_key = section_to_view.lower().replace(' ', '_')
                    if section_key in proposal:
                        print(f"\n{'-'*70}")
                        print(proposal[section_key])
                        print(f"{'-'*70}")
            
            elif choice == '3':
                # View feedback history
                print(f"\n📜 FEEDBACK HISTORY ({len(self.feedback_system.feedback_history)} rounds):\n")
                for i, fb in enumerate(self.feedback_system.feedback_history, 1):
                    print(f"Round {i}: {fb['timestamp']}")
                    print(f"  Rating: {fb.get('overall_rating', 'N/A')}/5")
                    print(f"  Sections revised: {sum(1 for d in fb.get('sections', {}).values() if d.get('status') == 'needs_revision')}")
                    print()
            
            elif choice == '4':
                # Compare versions
                if len(self.feedback_system.versions) < 2:
                    print("⚠️  Need at least 2 versions to compare")
                else:
                    print(f"\nAvailable versions: 1 to {len(self.feedback_system.versions)}")
                    try:
                        v1 = int(input("First version: ").strip()) - 1
                        v2 = int(input("Second version: ").strip()) - 1
                        self.feedback_system.compare_versions(v1, v2)
                    except ValueError:
                        print("❌ Invalid input")
            
            elif choice == '5':
                # Export version
                filename = input("Export filename (e.g., proposal_v2.json): ").strip()
                if not filename:
                    filename = f"proposal_refined_v{round_number}.json"
                
                with open(filename, 'w') as f:
                    json.dump(self.current_version, f, indent=2)
                print(f"✅ Exported: {filename}")
            
            elif choice == '6':
                # Finish
                print("\n" + "="*70)
                print("💾 SAVING FINAL VERSION")
                print("="*70)
                
                # Save final version
                with open('proposal_final.json', 'w') as f:
                    json.dump(self.current_version, f, indent=2)
                
                # Save feedback report
                self.feedback_system.generate_feedback_report('feedback_report.txt')
                
                print("\n✅ Session complete!")
                print("   Files saved:")
                print("   - proposal_final.json")
                print("   - feedback_report.txt")
                break
            
            else:
                print("❌ Invalid option")

# ==================== CLI ====================

def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Interactive proposal refinement")
    parser.add_argument("proposal_json", help="Input proposal JSON file")
    parser.add_argument("-m", "--mode", choices=['interactive', 'auto'], default='interactive',
                       help="Feedback mode")
    
    args = parser.parse_args()
    
    # Load proposal
    with open(args.proposal_json, 'r') as f:
        proposal_data = json.load(f)
    
    if args.mode == 'interactive':
        # Run interactive session
        session = InteractiveFeedbackSession(proposal_data)
        session.run()
    else:
        # Single feedback round
        system = FeedbackSystem()
        feedback = system.collect_feedback(proposal_data, interactive=True)
        refined = system.refine_proposal(proposal_data, feedback)
        
        # Save
        with open('proposal_refined.json', 'w') as f:
            json.dump(refined, f, indent=2)
        
        print("✅ Refined proposal saved: proposal_refined.json")


if __name__ == "__main__":
    main()