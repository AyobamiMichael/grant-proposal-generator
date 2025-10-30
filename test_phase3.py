"""
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
print("\n1. Testing Innovator Agent...")
try:
    innovator = InnovatorAgent(queue, llm)
    print(f"   ✅ {innovator.name} initialized")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Writer
print("\n2. Testing Writer Agent...")
try:
    writer = WriterAgent(queue, llm)
    print(f"   ✅ {writer.name} initialized")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n✅ Phase 3 agents working!")
print("\nNext: Run 'python demo_phase3.py'")
