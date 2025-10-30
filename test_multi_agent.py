"""
Multi-Agent System - Test Suite
Comprehensive tests for Phase 1 components
"""

import unittest
import time
from datetime import datetime
from demo_phase1 import (
    Message, MessageType, Priority, MessageQueue,
    BaseAgent, SupervisorAgent, MultiAgentSystem,
    AgentState
)


# ==================== TEST AGENTS ====================

class DummyAgent(BaseAgent):
    """Simple test agent for testing"""
    
    def __init__(self, name: str, message_queue: MessageQueue):
        super().__init__(name, "Test Agent", message_queue)
        self.processed_messages = []
    
    def process(self, message: Message):
        """Just log the message"""
        self.processed_messages.append(message)
        return {
            'status': 'processed',
            'message_id': message.message_id,
            'content': message.content
        }



class EchoAgent(BaseAgent):
    """Agent that echoes back messages"""
    
    def __init__(self, name: str, message_queue: MessageQueue):
        super().__init__(name, "Echo Agent", message_queue)
    
    def process(self, message: Message):
        """Echo the message back"""
        return {
            'echo': message.content,
            'sender': message.sender
        }



# ==================== MESSAGE TESTS ====================

class TestMessage(unittest.TestCase):
    """Test Message class"""
    
    def test_message_creation(self):
        """Test creating a message"""
        msg = Message(
            sender="agent1",
            recipient="agent2",
            message_type=MessageType.REQUEST,
            content={'data': 'test'}
        )
        
        self.assertEqual(msg.sender, "agent1")
        self.assertEqual(msg.recipient, "agent2")
        self.assertEqual(msg.message_type, MessageType.REQUEST)
        self.assertIsInstance(msg.timestamp, datetime)
        self.assertIsNotNone(msg.message_id)

    
    def test_message_priority(self):
        """Test message priority"""
        msg_low = Message(
            sender="a", recipient="b",
            message_type=MessageType.REQUEST,
            content={},
            priority=Priority.LOW
        )
        
        msg_urgent = Message(
            sender="a", recipient="b",
            message_type=MessageType.REQUEST,
            content={},
            priority=Priority.URGENT
        )
        
        self.assertEqual(msg_low.priority, Priority.LOW)
        self.assertEqual(msg_urgent.priority, Priority.URGENT)
    

    def test_message_serialization(self):
        """Test message to_dict"""
        msg = Message(
            sender="test",
            recipient="receiver",
            message_type=MessageType.RESPONSE,
            content={'result': 42}
        )
        
        msg_dict = msg.to_dict()
        
        self.assertIn('sender', msg_dict)
        self.assertIn('recipient', msg_dict)
        self.assertIn('content', msg_dict)
        self.assertEqual(msg_dict['content']['result'], 42)
    

class TestMessageQueue(unittest.TestCase):
    """Test MessageQueue class"""
    
    def setUp(self):
        """Create fresh queue for each test"""
        self.queue = MessageQueue()
    
    def test_send_and_receive(self):
        """Test basic send/receive"""
        msg = Message(
            sender="sender",
            recipient="receiver",
            message_type=MessageType.REQUEST,
            content={'test': 'data'}
        )
    
        self.queue.send(msg)
        received = self.queue.receive("receiver", timeout=1)
        
        self.assertIsNotNone(received)
        self.assertEqual(received.sender, "sender")
        self.assertEqual(received.content['test'], 'data')
    

    def test_priority_ordering(self):
        """Test that high priority messages come first"""
        # Send low priority first
        msg_low = Message(
            sender="s", recipient="r",
            message_type=MessageType.REQUEST,
            content={'priority': 'low'},
            priority=Priority.LOW
        )
        self.queue.send(msg_low)
        
        # Then send urgent
        msg_urgent = Message(
            sender="s", recipient="r",
            message_type=MessageType.REQUEST,
            content={'priority': 'urgent'},
            priority=Priority.URGENT
        )
        self.queue.send(msg_urgent)
        
        # Urgent should come out first
        first = self.queue.receive("r", timeout=1)
        self.assertEqual(first.content['priority'], 'urgent')
    

    def test_broadcast(self):
        """Test broadcasting to multiple recipients"""
        msg = Message(
            sender="broadcaster",
            recipient="dummy",  # Will be overridden
            message_type=MessageType.REQUEST,
            content={'broadcast': 'message'}
        )
        
        recipients = ["agent1", "agent2", "agent3"]
        self.queue.broadcast(msg, recipients)
        
        # Each agent should receive a message
        for agent in recipients:
            received = self.queue.receive(agent, timeout=1)
            self.assertIsNotNone(received)
            self.assertEqual(received.content['broadcast'], 'message')
    

    def test_message_history(self):
        """Test message history tracking"""
        for i in range(5):
            msg = Message(
                sender="sender",
                recipient="receiver",
                message_type=MessageType.REQUEST,
                content={'index': i}
            )
            self.queue.send(msg)
        
        history = self.queue.get_history(limit=10)
        self.assertEqual(len(history), 5)


# ==================== AGENT TESTS ====================

class TestBaseAgent(unittest.TestCase):
    """Test BaseAgent functionality"""
    
    def setUp(self):
        """Create queue and agent for each test"""
        self.queue = MessageQueue()
        self.agent = DummyAgent("test_agent", self.queue)
    
    def test_agent_initialization(self):
        """Test agent creation"""
        self.assertEqual(self.agent.name, "test_agent")
        self.assertEqual(self.agent.role, "Test Agent")
        self.assertEqual(self.agent.state, AgentState.IDLE)


    def test_send_message(self):
        """Test agent sending message"""
        self.agent.send_message(
            recipient="other_agent",
            message_type=MessageType.REQUEST,
            content={'test': 'data'}
        )
        
        # Check message was queued
        received = self.queue.receive("other_agent", timeout=1)
        self.assertIsNotNone(received)
        self.assertEqual(received.sender, "test_agent")
    

    def test_send_response(self):
        """Test agent responding to message"""
        original = Message(
            sender="requester",
            recipient="test_agent",
            message_type=MessageType.REQUEST,
            content={'query': 'test'},
            requires_response=True
        )
        
        self.agent.send_response(original, {'answer': '42'})
        
        # Check response was sent
        response = self.queue.receive("requester", timeout=1)
        self.assertIsNotNone(response)
        self.assertEqual(response.message_type, MessageType.RESPONSE)
        self.assertIn('response', response.content)

    
    def test_agent_threading(self):
        """Test agent runs in thread"""
        self.agent.start()
        time.sleep(0.5)
        
        # Agent should be alive
        self.assertTrue(self.agent._thread.is_alive())
        
        # Send a message
        msg = Message(
            sender="sender",
            recipient="test_agent",
            message_type=MessageType.REQUEST,
            content={'data': 'test'}
        )
        self.queue.send(msg)
        
        # Wait for processing
        time.sleep(0.5)
        
        # Check it was processed
        self.assertGreater(len(self.agent.processed_messages), 0)
        
        # Stop agent
        self.agent.stop()
        time.sleep(0.5)
        self.assertEqual(self.agent.state, AgentState.STOPPED)
    

    def test_agent_status(self):
        """Test getting agent status"""
        status = self.agent.get_status()
        
        self.assertIn('name', status)
        self.assertIn('role', status)
        self.assertIn('state', status)
        self.assertIn('messages_processed', status)
        self.assertIn('error_count', status)
    
    def tearDown(self):
        """Clean up agent"""
        if self.agent._thread and self.agent._thread.is_alive():
            self.agent.stop()



class TestSupervisorAgent(unittest.TestCase):
    """Test SupervisorAgent functionality"""
    
    def setUp(self):
        """Create queue and supervisor"""
        self.queue = MessageQueue()
        self.supervisor = SupervisorAgent(self.queue)

    

    def test_supervisor_initialization(self):
        """Test supervisor creation"""
        self.assertEqual(self.supervisor.name, "supervisor")
        self.assertEqual(len(self.supervisor.registered_agents), 0)
        self.assertEqual(len(self.supervisor.active_tasks), 0)

    
    def test_agent_registration(self):
        """Test registering agents"""
        self.supervisor.register_agent("analyst", "Analysis Agent")
        self.supervisor.register_agent("evaluator", "Evaluation Agent")
        
        self.assertEqual(len(self.supervisor.registered_agents), 2)
        self.assertIn("analyst", self.supervisor.registered_agents)
    

    def test_task_routing(self):
        """Test routing tasks to agents"""
        # Register agents
        self.supervisor.register_agent("analyst", "Analyst")
        self.supervisor.register_agent("evaluator", "Evaluator")
        
        # Create a task
        task_id = "task_123"
        self.supervisor.active_tasks[task_id] = {
            'task_id': task_id,
            'status': 'active',
            'assigned_agents': []
        }


       # Route to agents
        self.supervisor.route_task_to_agents(
            task_id=task_id,
            agent_names=["analyst", "evaluator"],
            action="analyze",
            data={'paper': 'test.pdf'}
        )
        
        # Check messages were sent
        analyst_msg = self.queue.receive("analyst", timeout=1)
        evaluator_msg = self.queue.receive("evaluator", timeout=1)
        
        self.assertIsNotNone(analyst_msg)
        self.assertIsNotNone(evaluator_msg)
        self.assertEqual(analyst_msg.content['action'], 'analyze')

    def test_task_completion(self):
        """Test completing a task"""
        task_id = "task_456"
        self.supervisor.active_tasks[task_id] = {
            'task_id': task_id,
            'status': 'active'
        }
        
        self.supervisor.complete_task(task_id)
        
        # Should move to completed
        self.assertNotIn(task_id, self.supervisor.active_tasks)
        self.assertEqual(len(self.supervisor.completed_tasks), 1)
        self.assertEqual(self.supervisor.completed_tasks[0]['status'], 'completed')


    def tearDown(self):
        """Clean up supervisor"""
        if self.supervisor._thread and self.supervisor._thread.is_alive():
            self.supervisor.stop()



# ==================== SYSTEM TESTS ====================

class TestMultiAgentSystem(unittest.TestCase):
    """Test MultiAgentSystem integration"""
    
    def setUp(self):
        """Create system for each test"""
        self.system = MultiAgentSystem()
    

    def test_system_initialization(self):
        """Test system creation"""
        self.assertIsNotNone(self.system.message_queue)
        self.assertIsNotNone(self.system.supervisor)
        self.assertIn('supervisor', self.system.agents)
    
    def test_agent_registration(self):
        """Test registering new agents"""
        test_agent = DummyAgent("test1", self.system.message_queue)
        self.system.register_agent(test_agent)
        
        self.assertIn("test1", self.system.agents)
        self.assertIn("test1", self.system.supervisor.registered_agents)
    

    def test_start_stop_agents(self):
        """Test starting and stopping all agents"""
        # Add test agent
        test_agent = DummyAgent("test2", self.system.message_queue)
        self.system.register_agent(test_agent)
        
        # Start all
        self.system.start_all_agents()
        time.sleep(0.5)
        
        # Check they're running
        for agent in self.system.agents.values():
            self.assertTrue(agent._thread.is_alive())
        
        # Stop all
        self.system.stop_all_agents()
        time.sleep(0.5)
        
        # Check they stopped
        for agent in self.system.agents.values():
            self.assertEqual(agent.state, AgentState.STOPPED)
    
    def test_submit_task(self):
        """Test submitting a task"""
        self.system.start_all_agents()
        time.sleep(0.5)
        
        task_id = self.system.submit_task(
            task_type='test_task',
            data={'test': 'data'}
        )
        
        self.assertIsNotNone(task_id)
        time.sleep(0.5)
        
        # Check supervisor received it
        self.assertGreater(len(self.system.supervisor.active_tasks), 0)
        
        self.system.stop_all_agents()

    
    def test_system_status(self):
        """Test getting system status"""
        status = self.system.get_system_status()
        
        self.assertIn('agents', status)
        self.assertIn('message_queue_size', status)
        self.assertIn('active_tasks', status)
        self.assertIn('completed_tasks', status)
    

    def test_message_history(self):
        """Test getting message history"""
        # Send some messages
        self.system.submit_task('task1', {})
        self.system.submit_task('task2', {})
        time.sleep(0.5)
        
        history = self.system.get_message_history(limit=10)
        self.assertGreater(len(history), 0)
        self.assertIsInstance(history[0], dict)
    
    def tearDown(self):
        """Clean up system"""
        self.system.stop_all_agents()

    
# ==================== INTEGRATION TESTS ====================
class TestAgentCommunication(unittest.TestCase):
    """Test agent-to-agent communication"""
    
    def setUp(self):
        """Create system with multiple agents"""
        self.queue = MessageQueue()
        self.agent1 = EchoAgent("echo1", self.queue)
        self.agent2 = EchoAgent("echo2", self.queue)
    
    def test_bidirectional_communication(self):
        """Test two agents communicating"""
        # Start agents
        self.agent1.start()
        self.agent2.start()
        time.sleep(0.5)

           # Agent 1 sends to Agent 2
        self.agent1.send_message(
            recipient="echo2",
            message_type=MessageType.REQUEST,
            content={'ping': 'from_agent1'},
            requires_response=True
        )
        
        time.sleep(0.5)
        
        # Check agent2 processed it
        self.assertGreater(len(self.agent2.processing_history), 0)
        
        # Stop agents
        self.agent1.stop()
        self.agent2.stop()
    
    def tearDown(self):
        """Clean up agents"""
        self.agent1.stop()
        self.agent2.stop()

# ==================== PERFORMANCE TESTS ====================

class TestPerformance(unittest.TestCase):
    """Test system performance"""
    
    def test_message_throughput(self):
        """Test how many messages/sec system can handle"""
        queue = MessageQueue()
        
        start_time = time.time()
        num_messages = 1000
        
        for i in range(num_messages):
            msg = Message(
                sender="sender",
                recipient="receiver",
                message_type=MessageType.REQUEST,
                content={'index': i}
            )
            queue.send(msg)
        
        elapsed = time.time() - start_time
        throughput = num_messages / elapsed
        
        print(f"\n📊 Throughput: {throughput:.0f} messages/sec")
        self.assertGreater(throughput, 100)  # Should handle >100 msg/sec


    def test_agent_response_time(self):
        """Test agent processing latency"""
        queue = MessageQueue()
        agent = DummyAgent("latency_test", queue)
        agent.start()
        time.sleep(0.5)
        
        # Send message and measure response time
        start_time = time.time()
        
        msg = Message(
            sender="tester",
            recipient="latency_test",
            message_type=MessageType.REQUEST,
            content={'test': 'data'}
        )
        queue.send(msg)
        
        # Wait for processing
        time.sleep(0.2)
        
        elapsed = time.time() - start_time
        
        print(f"\n⏱️  Agent response time: {elapsed*1000:.2f}ms")
        self.assertLess(elapsed, 1.0)  # Should respond within 1 second
        
        agent.stop()
    

# ==================== RUN TESTS ====================

def run_tests():
    """Run all tests with verbose output"""
    
    print("="*60)
    print("🧪 MULTI-AGENT SYSTEM - TEST SUITE")
    print("="*60)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

      # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMessage))
    suite.addTests(loader.loadTestsFromTestCase(TestMessageQueue))
    suite.addTests(loader.loadTestsFromTestCase(TestBaseAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestSupervisorAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiAgentSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentCommunication))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)