"""
setup_phase3.py
Automated setup for Phase 3
"""

import os
import sys


def print_header():
    print("="*70)
    print("🚀 PHASE 3 SETUP - Complete System")
    print("="*70)
    print()

def check_phase2_files():
    """Check if Phase 2 is properly set up"""
    print("🔍 Checking Phase 2 files...")
    
    required_files = {
        'demo_phase1.py': '.',
        'demo_phase2.py': '.',
        'llm_wrapper.py': 'tools',
        'pdf_reader.py': 'tools',
        'analyst_agent.py': 'agents',
        'evaluator_agent.py': 'agents',
        '__init__.py (tools)': 'tools',
        '__init__.py (agents)': 'agents'
    }
    
    missing = []
    
    for file_desc, directory in required_files.items():
        if '__init__.py' in file_desc:
            file_path = os.path.join(directory, '__init__.py')
        else:
            file_path = os.path.join(directory, file_desc) if directory != '.' else file_desc
        
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} file(s)")
        print("   Please complete Phase 2 first!")
        return False
    
    print("\n✅ Phase 2 files present")
    return True

def check_new_agent_files():
    """Check if Phase 3 agent files exist"""
    print("\n🔍 Checking Phase 3 agent files...")
    
    new_agents = ['innovator_agent.py', 'writer_agent.py']
    
    all_exist = True
    for agent_file in new_agents:
        agent_path = os.path.join('agents', agent_file)
        if os.path.exists(agent_path):
            print(f"   ✅ {agent_path}")
        else:
            print(f"   ❌ {agent_path} - MISSING")
            print(f"      💡 Save the '{agent_file}' artifact to agents/ folder")
            all_exist = False
    
    if not all_exist:
        print("\n⚠️  Please save Phase 3 agent files first")
        return False
    
    print("\n✅ Phase 3 agent files present")
    return True
def update_agents_init():
    """Update agents/__init__.py to include new agents"""
    print("\n📝 Updating agents/__init__.py...")
    
    init_path = os.path.join('agents', '__init__.py')
    
    new_content = '''"""
agents package
Specialized AI agents for the multi-agent system
"""

from .analyst_agent import AnalystAgent
from .evaluator_agent import EvaluatorAgent
from .innovator_agent import InnovatorAgent
from .writer_agent import WriterAgent

__all__ = ['AnalystAgent', 'EvaluatorAgent', 'InnovatorAgent', 'WriterAgent']
'''
    
    try:
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"   ✅ Updated {init_path}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to update: {e}")
        return False

def check_demo_phase3():
    """Check if demo_phase3.py exists"""
    print("\n🔍 Checking demo_phase3.py...")
    
    if os.path.exists('demo_phase3.py'):
        print("   ✅ demo_phase3.py exists")
        return True
    else:
        print("   ❌ demo_phase3.py - MISSING")
        print("      💡 Save the 'demo_phase3.py' artifact to project root")
        return False


def test_imports():
    """Test if all imports work"""
    print("\n🧪 Testing imports...")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test Phase 1
    try:
        from demo_phase1 import MultiAgentSystem
        print("   ✅ Phase 1 imports")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Phase 1 failed: {e}")
        tests_failed += 1
    
    # Test Phase 2
    try:
        from tools.llm_wrapper import LLMWrapper
        from tools.pdf_reader import PDFReader
        from agents.analyst_agent import AnalystAgent
        from agents.evaluator_agent import EvaluatorAgent
        print("   ✅ Phase 2 imports")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Phase 2 failed: {e}")
        tests_failed += 1
    
    # Test Phase 3
    try:
        from agents.innovator_agent import InnovatorAgent
        from agents.writer_agent import WriterAgent
        print("   ✅ Phase 3 imports")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Phase 3 failed: {e}")
        tests_failed += 1
    
    return tests_passed, tests_failed


def create_quick_test():
    """Create a quick test script"""
    print("\n📝 Creating quick test script...")
    
    test_content = '''"""
test_phase3.py
Quick test for Phase 3 system
"""

from agents.innovator_agent import InnovatorAgent
from agents.writer_agent import WriterAgent
from tools.llm_wrapper import LLMWrapper
from demo_phase1 import MessageQueue

print("Testing Phase 3 agents...")

# Initialize
llm = LLMWrapper(model='fast')
queue = MessageQueue()

# Test Innovator
print("\\n1. Testing Innovator Agent...")
try:
    innovator = InnovatorAgent(queue, llm)
    print(f"   ✅ {innovator.name} initialized")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Writer
print("\\n2. Testing Writer Agent...")
try:
    writer = WriterAgent(queue, llm)
    print(f"   ✅ {writer.name} initialized")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\\n✅ Phase 3 agents working!")
print("\\nNext: Run 'python demo_phase3.py'")
'''
    
    try:
        with open('test_phase3.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("   ✅ Created test_phase3.py")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def print_next_steps(all_checks_passed):
    """Print next steps"""
    print("\n" + "="*70)
    print("📊 SETUP SUMMARY")
    print("="*70)
    
    if all_checks_passed:
        print("\n🎉 ALL CHECKS PASSED!")
        print("\nYour Phase 3 system is ready!")
        print("\nNext steps:")
        print("  1. Run quick test: python test_phase3.py")
        print("  2. Run full demo: python demo_phase3.py")
        print("  3. Choose option 2 (Mock Demo) to test without PDF")
        print("  4. Or provide your own PDF for full analysis")
        print("\n✨ Enjoy your complete multi-agent system!")
    else:
        print("\n⚠️  SETUP INCOMPLETE")
        print("\nPlease fix the issues above:")
        print("  1. Save Phase 3 agent files (innovator_agent.py, writer_agent.py)")
        print("  2. Save demo_phase3.py to project root")
        print("  3. Run this setup script again")
        print("\nArtifacts to save:")
        print("  - agents/innovator_agent.py")
        print("  - agents/writer_agent.py")
        print("  - demo_phase3.py")
    
    print("="*70)

def main():
    """Run Phase 3 setup"""
    
    print_header()
    
    # Check we're in right directory
    if not os.path.exists('demo_phase1.py'):
        print("❌ Error: demo_phase1.py not found!")
        print("   Run this script from the project root directory")
        return False
    
    print("✅ Running from project root")
    print()
    
    # Run checks
    checks = {
        'Phase 2 Files': check_phase2_files(),
        'Phase 3 Agent Files': check_new_agent_files(),
        'demo_phase3.py': check_demo_phase3()
    }
    
    # Update init file if agents exist
    if checks['Phase 3 Agent Files']:
        checks['agents/__init__.py Update'] = update_agents_init()
    
    # Test imports if all files present
    if all(checks.values()):
        tests_passed, tests_failed = test_imports()
        checks['Import Tests'] = (tests_failed == 0)
        
        # Create test script
        if checks['Import Tests']:
            checks['Test Script Creation'] = create_quick_test()
    
    # Summary
    all_passed = all(checks.values())
    print_next_steps(all_passed)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)