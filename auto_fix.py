"""
auto_fix.py
AUTOMATED FIX - Solves all import issues automatically

Just run: python auto_fix.py
"""

import os
import sys
from pathlib import Path


def print_header():
    print("="*60)
    print("🔧 AUTOMATED FIX - Phase 2 Import Issues")
    print("="*60)
    print()


def create_tools_init():
    """Create tools/__init__.py"""
    
    content = '''"""
tools package
Utility tools for the multi-agent system
"""

from .llm_wrapper import LLMWrapper, create_llm
from .pdf_reader import PDFReader

__all__ = ['LLMWrapper', 'create_llm', 'PDFReader']
'''
    
    # Ensure tools directory exists
    os.makedirs('tools', exist_ok=True)
    
    # Write file
    init_path = os.path.join('tools', '__init__.py')
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return init_path


def create_agents_init():
    """Create agents/__init__.py"""
    
    content = '''"""
agents package
Specialized AI agents for the multi-agent system
"""

from .analyst_agent import AnalystAgent
from .evaluator_agent import EvaluatorAgent

__all__ = ['AnalystAgent', 'EvaluatorAgent']
'''
    
    # Ensure agents directory exists
    os.makedirs('agents', exist_ok=True)
    
    # Write file
    init_path = os.path.join('agents', '__init__.py')
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return init_path


def fix_analyst_agent():
    """Fix imports in analyst_agent.py"""
    
    agent_path = os.path.join('agents', 'analyst_agent.py')
    
    if not os.path.exists(agent_path):
        return None, "File not found"
    
    with open(agent_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the sys.path.append line
    old_import = """import sys
sys.path.append('..')

from demo_phase1 import BaseAgent, Message, MessageType"""
    
    new_import = """import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo_phase1 import BaseAgent, Message, MessageType"""
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        
        with open(agent_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return agent_path, "Fixed"
    
    return agent_path, "Already OK"


def fix_evaluator_agent():
    """Fix imports in evaluator_agent.py"""
    
    agent_path = os.path.join('agents', 'evaluator_agent.py')
    
    if not os.path.exists(agent_path):
        return None, "File not found"
    
    with open(agent_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the sys.path.append line
    old_import = """import sys
sys.path.append('..')

from demo_phase1 import BaseAgent, Message, MessageType"""
    
    new_import = """import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo_phase1 import BaseAgent, Message, MessageType"""
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        
        with open(agent_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return agent_path, "Fixed"
    
    return agent_path, "Already OK"


def test_imports():
    """Test if imports work now"""
    
    print("\n🧪 Testing imports...")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Import demo_phase1
    try:
        from demo_phase1 import MultiAgentSystem
        print("   ✅ demo_phase1 imports")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ demo_phase1 failed: {e}")
        tests_failed += 1
    
    # Test 2: Import tools.llm_wrapper
    try:
        from tools.llm_wrapper import LLMWrapper
        print("   ✅ tools.llm_wrapper imports")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ tools.llm_wrapper failed: {e}")
        tests_failed += 1
    
    # Test 3: Import tools.pdf_reader
    try:
        from tools.pdf_reader import PDFReader
        print("   ✅ tools.pdf_reader imports")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ tools.pdf_reader failed: {e}")
        tests_failed += 1
    
    # Test 4: Import agents.analyst_agent
    try:
        from agents.analyst_agent import AnalystAgent
        print("   ✅ agents.analyst_agent imports")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ agents.analyst_agent failed: {e}")
        tests_failed += 1
    
    # Test 5: Import agents.evaluator_agent
    try:
        from agents.evaluator_agent import EvaluatorAgent
        print("   ✅ agents.evaluator_agent imports")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ agents.evaluator_agent failed: {e}")
        tests_failed += 1
    
    return tests_passed, tests_failed


def main():
    """Run automated fix"""
    
    print_header()
    
    print("🔍 Checking current directory...")
    current_dir = os.getcwd()
    print(f"   Working in: {current_dir}")
    print()
    
    # Check if we're in the right place
    if not os.path.exists('demo_phase1.py'):
        print("❌ Error: demo_phase1.py not found!")
        print("   Make sure you're running this from the project root directory.")
        print()
        print("   Current directory:", current_dir)
        print("   Expected files: demo_phase1.py, demo_phase2.py, etc.")
        return False
    
    print("✅ Found demo_phase1.py - we're in the right place!")
    print()
    
    # Step 1: Create __init__.py files
    print("📝 Step 1: Creating __init__.py files...")
    
    tools_init = create_tools_init()
    print(f"   ✅ Created: {tools_init}")
    
    agents_init = create_agents_init()
    print(f"   ✅ Created: {agents_init}")
    
    print()
    
    # Step 2: Fix agent imports
    print("📝 Step 2: Fixing agent imports...")
    
    analyst_path, analyst_status = fix_analyst_agent()
    if analyst_path:
        print(f"   ✅ {analyst_path}: {analyst_status}")
    else:
        print(f"   ⚠️  analyst_agent.py: {analyst_status}")
    
    evaluator_path, evaluator_status = fix_evaluator_agent()
    if evaluator_path:
        print(f"   ✅ {evaluator_path}: {evaluator_status}")
    else:
        print(f"   ⚠️  evaluator_agent.py: {evaluator_status}")
    
    print()
    
    # Step 3: Test imports
    tests_passed, tests_failed = test_imports()
    
    print()
    print("="*60)
    print("📊 FIX SUMMARY")
    print("="*60)
    print(f"Tests Passed: {tests_passed}/5")
    print(f"Tests Failed: {tests_failed}/5")
    print()
    
    if tests_failed == 0:
        print("🎉 SUCCESS! All imports working!")
        print()
        print("Next steps:")
        print("  1. Run: python demo_phase2.py")
        print("  2. Choose option 2 (Mock Demo)")
        print("  3. Enjoy! 🚀")
        print()
        return True
    else:
        print("⚠️  Some imports still failing.")
        print()
        print("Troubleshooting:")
        print("  1. Make sure all files are in correct locations")
        print("  2. Check that tools/ and agents/ directories exist")
        print("  3. Try: pip install -r requirements.txt")
        print("  4. Check for typos in file names")
        print()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)