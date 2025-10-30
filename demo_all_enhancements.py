"""
demo_all_enhancements.py
Quick test of all enhancements
"""

def test_enhancements():
    """Test all enhancements are working"""
    
    print("="*70)
    print("🧪 TESTING ALL ENHANCEMENTS")
    print("="*70)
    print()
    
    # Test 1: Gradio
    print("1. Gradio Web UI")
    try:
        from app_gradio import GradioApp
        app = GradioApp()
        print("   ✅ Gradio ready")
        print("   Run: python app_gradio.py")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    # Test 2: Batch Processing
    print("2. Batch Processing")
    try:
        from batch_processor import BatchProcessor
        processor = BatchProcessor()
        print("   ✅ Batch processor ready")
        print("   Run: python batch_processor.py papers_folder/")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    # Test 3: Export
    print("3. Export Formats")
    try:
        from export_formats import ProposalExporter
        exporter = ProposalExporter()
        print("   ✅ Exporter ready")
        print("   Run: python export_formats.py proposal_data.json -f docx")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    # Test 4: Feedback
    print("4. Feedback Loop")
    try:
        from feedback_loop import FeedbackSystem
        feedback = FeedbackSystem()
        print("   ✅ Feedback system ready")
        print("   Run: python feedback_loop.py proposal_data.json")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    print("="*70)
    print("✅ All enhancements tested!")
    print("="*70)
    print()
    print("Quick Start:")
    print("  1. Generate proposal: python demo_phase3.py")
    print("  2. Launch Web UI: python app_gradio.py")
    print("  3. Try batch processing: python batch_processor.py folder/")
    print("  4. Export to DOCX: python export_formats.py data.json -f docx")
    print("  5. Refine with feedback: python feedback_loop.py data.json")


if __name__ == "__main__":
    test_enhancements()
