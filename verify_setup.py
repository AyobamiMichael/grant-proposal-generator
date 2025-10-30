"""
verify_setup.py
Verify Phase 2 setup and dependencies (UPDATED WITH FIXED IMPORTS)
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version_str} (OK)")
        return True
    else:
        print(f"   ❌ Python {version_str} (Need >= 3.8)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking dependencies...")
    
    required = {
        'groq': '0.4.1',
        'pypdf': '3.17.4',
        'pydantic': '2.5.3',
        'dotenv': '1.0.0',
        'dateutil': '2.8.2'
    }
    
    all_ok = True
    
    for package, version in required.items():
        try:
            if package == 'dotenv':
                import dotenv
                pkg = dotenv
                pkg_name = 'python-dotenv'
            elif package == 'dateutil':
                import dateutil
                pkg = dateutil
                pkg_name = 'python-dateutil'
            else:
                pkg = __import__(package)
                pkg_name = package
            
            installed_version = getattr(pkg, '__version__', 'unknown')
            print(f"   ✅ {pkg_name}: {installed_version}")
            
        except ImportError:
            print(f"   ❌ {pkg_name}: NOT INSTALLED")
            all_ok = False
    
    return all_ok


def check_env_file():
    """Check if .env file exists and has API key"""
    print("\n🔑 Checking .env file...")
    
    if not os.path.exists('.env'):
        print("   ❌ .env file not found")
        print("   📝 Create .env with: GROQ_API_KEY=\"your_key_here\"")
        return False
    
    print("   ✅ .env file exists")
    
    # Try to load
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("   ❌ GROQ_API_KEY not found in .env")
        return False
    
    if not api_key.startswith('gsk_'):
        print("   ⚠️  GROQ_API_KEY doesn't look valid (should start with 'gsk_')")
        return False
    
    print(f"   ✅ GROQ_API_KEY found (starts with {api_key[:10]}...)")
    return True


def check_groq_connection():
    """Test Groq API connection"""
    print("\n🌐 Testing Groq API connection...")
    
    try:
        from groq import Groq
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY')
        
        if not api_key:
            print("   ❌ No API key to test")
            return False
        
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": "Reply with just 'OK'"}
            ],
            max_tokens=10,
            temperature=0.0
        )
        
        result = response.choices[0].message.content.strip()
        
        if 'OK' in result or 'ok' in result.lower():
            print(f"   ✅ Groq API working! Response: '{result}'")
            return True
        else:
            print(f"   ⚠️  Unexpected response: '{result}'")
            return True  # Still working
            
    except Exception as e:
        print(f"   ❌ Groq API error: {e}")
        return False


def check_project_structure():
    """Check if all required files exist"""
    print("\n📂 Checking project structure...")
    
    required_files = {
        'demo_phase1.py': '.',
        'demo_phase2.py': '.',
        'requirements.txt': '.',
        'llm_wrapper.py': 'tools',
        'pdf_reader.py': 'tools',
        'analyst_agent.py': 'agents',
        'evaluator_agent.py': 'agents',
        '__init__.py (tools)': 'tools',
        '__init__.py (agents)': 'agents'
    }
    
    all_ok = True
    
    for file_desc, directory in required_files.items():
        if '__init__.py' in file_desc:
            file_path = os.path.join(directory, '__init__.py')
            display_name = f"{directory}/__init__.py"
        else:
            file_path = os.path.join(directory, file_desc) if directory != '.' else file_desc
            display_name = file_path
        
        if os.path.exists(file_path):
            print(f"   ✅ {display_name}")
        else:
            print(f"   ❌ {display_name} not found")
            all_ok = False
            
            if '__init__.py' in file_path:
                print(f"      💡 Fix: Run 'python auto_fix.py' to create it")
    
    return all_ok


def test_phase1():
    """Test Phase 1 components"""
    print("\n🧪 Testing Phase 1 components...")
    
    try:
        from demo_phase1 import MultiAgentSystem, Message, MessageType
        
        # Create system
        system = MultiAgentSystem()
        print("   ✅ MultiAgentSystem initialized")
        
        # Test message creation
        msg = Message(
            sender="test",
            recipient="supervisor",
            message_type=MessageType.REQUEST,
            content={"test": "data"}
        )
        print("   ✅ Message creation works")
        
        # Test message queue
        system.message_queue.send(msg)
        received = system.message_queue.receive("supervisor", timeout=0.1)
        
        if received:
            print("   ✅ Message queue works")
        else:
            print("   ❌ Message queue issue")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Phase 1 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_phase2():
    """Test Phase 2 components with proper imports"""
    print("\n🧪 Testing Phase 2 components...")
    
    try:
        # Import from packages (with __init__.py)
        from tools.llm_wrapper import LLMWrapper
        print("   ✅ LLM wrapper imports")
        
        from tools.pdf_reader import PDFReader
        print("   ✅ PDF reader imports")
        
        from agents.analyst_agent import AnalystAgent
        print("   ✅ Analyst agent imports")
        
        from agents.evaluator_agent import EvaluatorAgent
        print("   ✅ Evaluator agent imports")
        
        # Test initialization
        llm = LLMWrapper(model='fast')
        print("   ✅ LLM wrapper initializes")
        
        reader = PDFReader()
        print("   ✅ PDF reader initializes")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        print("\n   💡 Fix: Missing __init__.py files?")
        print("      Run: python auto_fix.py")
        return False
        
    except Exception as e:
        print(f"   ❌ Phase 2 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_summary(results):
    """Print summary of checks"""
    print("\n" + "="*60)
    print("📊 SETUP VERIFICATION SUMMARY")
    print("="*60)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("\nYou're ready to use Phase 2!")
        print("\nNext steps:")
        print("  1. Run: python demo_phase2.py")
        print("  2. Choose option 2 (Mock Demo) to test without PDF")
        print("  3. Or provide your own PDF for full analysis")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("\nFix the issues above and run this script again.")
        print("\nCommon fixes:")
        print("  • Missing __init__.py? Run: python auto_fix.py")
        print("  • Install dependencies: pip install -r requirements.txt")
        print("  • Create .env file with your GROQ_API_KEY")
        print("  • Check file structure matches README")
    
    print("="*60)
    
    return all_passed


def main():
    """Run all verification checks"""
    print("="*60)
    print("🔍 PHASE 2 SETUP VERIFICATION")
    print("="*60)
    
    results = {}
    
    # Run checks
    results['Python Version'] = check_python_version()
    results['Dependencies'] = check_dependencies()
    results['Environment File'] = check_env_file()
    results['Groq Connection'] = check_groq_connection()
    results['Project Structure'] = check_project_structure()
    results['Phase 1 Components'] = test_phase1()
    results['Phase 2 Components'] = test_phase2()
    
    # Summary
    success = print_summary(results)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)