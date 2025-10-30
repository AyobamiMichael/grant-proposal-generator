"""
setup_enhancements.py
Setup and verify all optional enhancements
"""

import os
import sys
import subprocess


def print_header():
    print("="*70)
    print("🎨 ENHANCEMENTS SETUP - All 4 Features")
    print("="*70)
    print()


def check_phase3():
    """Check if Phase 3 is set up"""
    print("🔍 Checking Phase 3 system...")
    
    required_files = [
        'demo_phase3.py',
        'agents/innovator_agent.py',
        'agents/writer_agent.py'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            missing.append(file)
    
    if missing:
        print("\n⚠️  Phase 3 not complete!")
        print("   Please complete Phase 3 before installing enhancements")
        return False
    
    print("\n✅ Phase 3 ready")
    return True


def check_enhancement_files():
    """Check if enhancement files are present"""
    print("\n🔍 Checking enhancement files...")
    
    enhancement_files = {
        'app_gradio.py': 'Enhancement 1: Web UI',
        'batch_processor.py': 'Enhancement 2: Batch Processing',
        'export_formats.py': 'Enhancement 3: Export DOCX/PDF',
        'feedback_loop.py': 'Enhancement 4: Feedback Loop'
    }
    
    missing = []
    for file, description in enhancement_files.items():
        if os.path.exists(file):
            print(f"   ✅ {file} ({description})")
        else:
            print(f"   ❌ {file} - MISSING")
            print(f"      💡 Save '{file}' artifact to project root")
            missing.append(file)
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} file(s)")
        print("   Please save the enhancement artifacts first")
        return False
    
    print("\n✅ All enhancement files present")
    return True


def install_dependencies():
    """Install enhancement dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Check if requirements file exists
    if not os.path.exists('requirements_enhancements.txt'):
        print("   ⚠️  requirements_enhancements.txt not found")
        print("   Installing individual packages...")
        
        packages = [
            'gradio==4.44.0',
            'python-docx==1.1.0',
            'reportlab==4.2.0'
        ]
        
        for package in packages:
            print(f"\n   Installing {package}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"   ✅ {package} installed")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to install {package}: {e}")
                return False
    else:
        print("   Installing from requirements_enhancements.txt...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                '-r', 'requirements_enhancements.txt'
            ])
            print("   ✅ All dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Installation failed: {e}")
            return False
    
    print("\n✅ Dependencies installed")
    return True


def test_imports():
    """Test if enhancements can be imported"""
    print("\n🧪 Testing imports...")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test Enhancement 1: Gradio
    print("\n   Testing Enhancement 1: Gradio Web UI...")
    try:
        import gradio as gr
        from app_gradio import GradioApp
        print("   ✅ Gradio imports work")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Gradio import failed: {e}")
        tests_failed += 1
    
    # Test Enhancement 2: Batch Processing
    print("\n   Testing Enhancement 2: Batch Processing...")
    try:
        from batch_processor import BatchProcessor
        print("   ✅ Batch processor imports work")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Batch processor import failed: {e}")
        tests_failed += 1
    
    # Test Enhancement 3: Export
    print("\n   Testing Enhancement 3: Export Formats...")
    try:
        from docx import Document
        import reportlab
        from export_formats import ProposalExporter
        print("   ✅ Export tools import work")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Export import failed: {e}")
        tests_failed += 1
    
    # Test Enhancement 4: Feedback
    print("\n   Testing Enhancement 4: Feedback Loop...")
    try:
        from feedback_loop import FeedbackSystem
        print("   ✅ Feedback system imports work")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Feedback import failed: {e}")
        tests_failed += 1
    
    print(f"\n   Tests: {tests_passed}/4 passed")
    
    return tests_failed == 0


def create_demo_script():
    """Create a demo script for testing all enhancements"""
    print("\n📝 Creating demo script...")
    
    demo_content = '''"""
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
'''
    
    try:
        with open('demo_all_enhancements.py', 'w', encoding='utf-8') as f:
            f.write(demo_content)
        print("   ✅ Created demo_all_enhancements.py")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def print_next_steps(all_checks_passed):
    """Print next steps"""
    print("\n" + "="*70)
    print("📊 SETUP SUMMARY")
    print("="*70)
    print()
    
    if all_checks_passed:
        print("🎉 ALL ENHANCEMENTS READY!")
        print()
        print("Quick Start Guide:")
        print()
        print("1️⃣  Test all enhancements:")
        print("   python demo_all_enhancements.py")
        print()
        print("2️⃣  Launch Web UI:")
        print("   python app_gradio.py")
        print("   → Opens at http://localhost:7860")
        print()
        print("3️⃣  Process multiple papers:")
        print("   python batch_processor.py papers_folder/")
        print()
        print("4️⃣  Export to DOCX/PDF:")
        print("   python export_formats.py proposal_data.json -f docx")
        print()
        print("5️⃣  Interactive refinement:")
        print("   python feedback_loop.py proposal_data.json")
        print()
        print("📚 Documentation:")
        print("   README_ENHANCEMENTS.md - Complete guide")
        print()
        print("✨ Your system now has:")
        print("   ✅ Beautiful web interface")
        print("   ✅ Batch processing")
        print("   ✅ Professional document export")
        print("   ✅ Interactive refinement")
        print()
    else:
        print("⚠️  SETUP INCOMPLETE")
        print()
        print("Please fix the issues above:")
        print("  1. Save all enhancement files")
        print("  2. Install dependencies: pip install -r requirements_enhancements.txt")
        print("  3. Run this setup script again")
        print()
        print("Missing artifacts to save:")
        print("  - app_gradio.py")
        print("  - batch_processor.py")
        print("  - export_formats.py")
        print("  - feedback_loop.py")
        print("  - requirements_enhancements.txt")
    
    print("="*70)


def main():
    """Run enhancement setup"""
    
    print_header()
    
    # Check we're in right directory
    if not os.path.exists('demo_phase1.py'):
        print("❌ Error: Not in project root directory")
        print("   Run this from the multi_agent_system folder")
        return False
    
    print("✅ Running from project root")
    print()
    
    # Run checks
    checks = {}
    
    checks['Phase 3'] = check_phase3()
    if not checks['Phase 3']:
        print_next_steps(False)
        return False
    
    checks['Enhancement Files'] = check_enhancement_files()
    if not checks['Enhancement Files']:
        print_next_steps(False)
        return False
    
    # Ask before installing
    install = input("\n📦 Install enhancement dependencies? (y/n): ").strip().lower()
    if install == 'y':
        checks['Dependencies'] = install_dependencies()
    else:
        print("   ⏭️  Skipping dependency installation")
        checks['Dependencies'] = False
    
    # Test imports if dependencies installed
    if checks.get('Dependencies', False):
        checks['Import Tests'] = test_imports()
    
    # Create demo script
    checks['Demo Script'] = create_demo_script()
    
    # Summary
    all_passed = all(checks.values())
    print_next_steps(all_passed)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)