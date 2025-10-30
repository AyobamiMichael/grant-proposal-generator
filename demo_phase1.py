"""
Multi-Agent System - Phase 1: Foundation
Base Agent Architecture + Supervisor + Message Queue

Project: AI Research Paper Analysis & Grant Proposal Generator
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import queue
import threading
import time
import json
from collections import defaultdict


# =============================== MESSAGE SYSTEM ======================

class MessageType(Enum):
    """Types of messages agents can send"""
    REQUEST = "request"
    RESPONSE= "response"
    QUERY = "query"
    CONFLICT = "conflict"
    ACKNOWLEDGMENT = "ack"
    ERROR ="error"

class Priority(Enum):
    """Message priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

@dataclass
class Message:
    """Message passed between agents"""
    sender: str
    recipient: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: Priority = Priority.MEDIUM
    message_id: str = field(default_factory=lambda: f"msg_{int(time.time()*1000)}")
    requires_response: bool = False

    def to_dict(self) -> dict:
        """Serialize message"""
        return {
            'message_id': self.message_id,
            'sender': self.sender,
            'recipient': self.recipient,
            'type': self.message_type.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority.value,
            'requires_response': self.requires_response
        }
    
    def __repr__(self):
        return f"Message({self.sender}→{self.recipient}: {self.message_type.value})"
    

class MessageQueue:
    """Central message queue for agent communication"""

    def __init__(self):
        self.queues: Dict[str, queue.PriorityQueue] = defaultdict(queue.PriorityQueue)
        self.message_history: List[Message] = []
        self.lock = threading.Lock()
        self._running = False
    
    def send(self, message: Message):
        """Send message to recipient's queue"""
        with self.lock:
            # Add to recipient's queue (priority queue: lower number = higher priority)
            priority_value = 6 - message.priority.value  # Invert for PriorityQueue
            self.queues[message.recipient].put((priority_value, message))
            
            # Log to history
            self.message_history.append(message)
            
            print(f"📨 {message.sender} → {message.recipient}: {message.message_type.value}")

    def receive(self, agent_name: str, timeout: float = 0.1) -> Optional[Message]:
        """Receive message from agent's queue (non-blocking)"""
        try:
            priority, message = self.queues[agent_name].get(timeout=timeout)
            return message
        except queue.Empty:
            return None
    
    def broadcast(self, message: Message, recipients: List[str]):
        """Send message to multiple recipients"""
        for recipient in recipients:
            msg = Message(
                sender=message.sender,
                recipient=recipient,
                message_type=message.message_type,
                content=message.content.copy(),
                priority=message.priority
            )
            self.send(msg)
    
    def get_history(self, limit: int = 50) -> List[Message]:
        """Get recent message history"""
        return self.message_history[-limit:]
    
    def clear_queue(self, agent_name: str):
        """Clear all messages for an agent"""
        with self.lock:
            self.queues[agent_name] = queue.PriorityQueue()

#=========================== BASE AGENT ============================

class AgentState(Enum):
    """Agent operational states"""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    STOPPED = "stopped"

class BaseAgent(ABC):
    """Abstract base class for all agents"""


    def __init__(self, name: str, role: str, message_queue: MessageQueue):
        self.name = name
        self.role = role
        self.message_queue = message_queue
        self.state = AgentState.IDLE
        self.processing_history: List[Dict] = []
        self.error_count = 0
        self._stop_flag = False
        self._thread: Optional[threading.Thread] = None
        
        print(f"✅ {self.name} ({self.role}) initialized")
    
    @abstractmethod
    def process(self, message: Message) -> Dict[str, Any]:
        """
        Process incoming message and return result
        Must be implemented by each agent
        """
        pass
    
    def send_message(self, recipient: str, message_type: MessageType, 
                     content: Dict[str, Any], priority: Priority = Priority.MEDIUM,
                     requires_response: bool = False):
        """Send message to another agent"""
        message = Message(
            sender=self.name,
            recipient=recipient,
            message_type=message_type,
            content=content,
            priority=priority,
            requires_response=requires_response
        )
        self.message_queue.send(message)
    
    
    def send_response(self, original_message: Message, response_content: Dict[str, Any]):
        """Send response to a request"""
        self.send_message(
            recipient=original_message.sender,
            message_type=MessageType.RESPONSE,
            content={
                'original_message_id': original_message.message_id,
                'response': response_content
            },
            priority=original_message.priority
        )
    

    def send_error(self, recipient: str, error_message: str):
        """Send error message"""
        self.send_message(
            recipient=recipient,
            message_type=MessageType.ERROR,
            content={'error': error_message},
            priority=Priority.HIGH
        )
    

    def log_processing(self, message: Message, result: Any, success: bool = True):
        """Log processing result"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message_id': message.message_id,
            'sender': message.sender,
            'type': message.message_type.value,
            'success': success,
            'result_summary': str(result)[:100]
        }
        self.processing_history.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.processing_history) > 100:
            self.processing_history = self.processing_history[-100:]
    

    def run(self):
        """Main agent loop (runs in separate thread)"""
        print(f"🏃 {self.name} starting main loop...")
        
        while not self._stop_flag:
            try:
                # Check for incoming messages
                message = self.message_queue.receive(self.name)
                
                if message:
                    print(f"📬 {self.name} received: {message.message_type.value} from {message.sender}")
                    
                    # Update state
                    self.state = AgentState.PROCESSING
                    
                    # Process message
                    try:
                        result = self.process(message)
                        self.log_processing(message, result, success=True)
                        
                        # Send response if required
                        if message.requires_response:
                            self.send_response(message, result)
                        
                    except Exception as e:
                        print(f"❌ {self.name} error: {e}")
                        self.error_count += 1
                        self.state = AgentState.ERROR
                        self.log_processing(message, str(e), success=False)
                        self.send_error(message.sender, str(e))
                    
                    # Return to idle
                    self.state = AgentState.IDLE
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.1)
                
            except Exception as e:
                print(f"💥 {self.name} critical error in main loop: {e}")
                self.state = AgentState.ERROR
                time.sleep(1)
        
        self.state = AgentState.STOPPED
        print(f"🛑 {self.name} stopped")
    

    def start(self):
        """Start agent in separate thread"""
        if self._thread is None or not self._thread.is_alive():
            self._stop_flag = False
            self._thread = threading.Thread(target=self.run, daemon=True)
            self._thread.start()
            print(f"▶️ {self.name} thread started")
    

    def stop(self):
        """Stop agent gracefully"""
        print(f"⏸️ Stopping {self.name}...")
        self._stop_flag = True
        if self._thread:
            self._thread.join(timeout=5)
    
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'name': self.name,
            'role': self.role,
            'state': self.state.value,
            'messages_processed': len(self.processing_history),
            'error_count': self.error_count,
            'is_alive': self._thread.is_alive() if self._thread else False
        }

# ==================== SUPERVISOR AGENT ====================

class SupervisorAgent(BaseAgent):
    """
    Orchestrator agent that manages workflow and routes tasks
    """
    
    def __init__(self, message_queue: MessageQueue):
        super().__init__(
            name="supervisor",
            role="Orchestrator & Workflow Manager",
            message_queue=message_queue
        )

         # Track active tasks
        self.active_tasks: Dict[str, Dict] = {}
        self.completed_tasks: List[Dict] = []
        
        # Agent registry
        self.registered_agents: Dict[str, str] = {}  # name -> role

    def register_agent(self, agent_name: str, agent_role: str):
        """Register an agent with the supervisor"""
        self.registered_agents[agent_name] = agent_role
        print(f"📋 Supervisor registered: {agent_name} ({agent_role})")

    
    def process(self, message: Message) -> Dict[str, Any]:
        """Process incoming messages and route tasks"""
        
        if message.message_type == MessageType.REQUEST:
            return self._handle_request(message)
        
        elif message.message_type == MessageType.RESPONSE:
            return self._handle_response(message)
        
        elif message.message_type == MessageType.CONFLICT:
            return self._handle_conflict(message)
        
        elif message.message_type == MessageType.ERROR:
            return self._handle_error(message)
        
        else:
            return {'status': 'unknown_message_type'}    
    

    def _handle_request(self, message: Message) -> Dict[str, Any]:
        """Handle new task request from user or agent"""
        
        task_type = message.content.get('task_type')
        task_id = f"task_{int(time.time()*1000)}"
        
        print(f"📥 Supervisor received task: {task_type}")
        
        # Create task record
        task = {
            'task_id': task_id,
            'task_type': task_type,
            'requester': message.sender,
            'status': 'active',
            'started_at': datetime.now().isoformat(),
            'assigned_agents': [],
            'responses_received': {},
            'data': message.content.get('data', {})
        }
        
        self.active_tasks[task_id] = task
        
        # Route to appropriate agents based on task type
        if task_type == 'analyze_paper':
            # This will be implemented in Phase 2
            # For now, acknowledge receipt
            return {
                'status': 'acknowledged',
                'task_id': task_id,
                'message': 'Task queued for processing'
            }
        
        elif task_type == 'generate_proposal':
            return {
                'status': 'acknowledged',
                'task_id': task_id,
                'message': 'Proposal generation initiated'
            }
        
        else:
            return {
                'status': 'error',
                'message': f'Unknown task type: {task_type}'
            }
    

    def _handle_response(self, message: Message) -> Dict[str, Any]:
        """Handle response from another agent"""
        
        original_msg_id = message.content.get('original_message_id')
        response = message.content.get('response')
        
        print(f"📨 Supervisor received response from {message.sender}")
        
        # Find the task this response belongs to
        for task_id, task in self.active_tasks.items():
            task['responses_received'][message.sender] = response
        
        return {'status': 'response_logged'}
    

    def _handle_conflict(self, message: Message) -> Dict[str, Any]:
        """Handle conflict between agents"""
        
        conflict_type = message.content.get('conflict_type')
        agents_involved = message.content.get('agents', [])
        
        print(f"⚠️ Conflict detected: {conflict_type} between {agents_involved}")
        
        # Conflict resolution logic (to be expanded in Phase 4)
        return {
            'status': 'conflict_acknowledged',
            'resolution': 'pending',
            'conflict_type': conflict_type
        }
    

    def _handle_error(self, message: Message) -> Dict[str, Any]:
        """Handle error from another agent"""
        
        error_msg = message.content.get('error')
        print(f"⚠️ Error from {message.sender}: {error_msg}")
        
        return {
            'status': 'error_logged',
            'agent': message.sender,
            'error': error_msg
        }
    

    def route_task_to_agents(self, task_id: str, agent_names: List[str], 
                             action: str, data: Dict[str, Any]):
        """Route a task to multiple agents"""
        
        if task_id not in self.active_tasks:
            print(f"❌ Task {task_id} not found")
            return
        
        task = self.active_tasks[task_id]
        
        for agent_name in agent_names:
            if agent_name not in self.registered_agents:
                print(f"⚠️ Agent {agent_name} not registered")
                continue
            
            # Send request to agent
            self.send_message(
                recipient=agent_name,
                message_type=MessageType.REQUEST,
                content={
                    'task_id': task_id,
                    'action': action,
                    'data': data
                },
                priority=Priority.HIGH,
                requires_response=True
            )
            
            task['assigned_agents'].append(agent_name)
        
        print(f"📤 Task {task_id} routed to {len(agent_names)} agents")
    
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        return self.active_tasks.get(task_id)
    

     
    def get_all_tasks(self) -> Dict[str, Dict]:
        """Get all active tasks"""
        return self.active_tasks
    
    def complete_task(self, task_id: str):
        """Mark task as complete"""
        if task_id in self.active_tasks:
            task = self.active_tasks.pop(task_id)
            task['status'] = 'completed'
            task['completed_at'] = datetime.now().isoformat()
            self.completed_tasks.append(task)
            print(f"✅ Task {task_id} completed")


# ==================== SYSTEM MANAGER ====================

class MultiAgentSystem:
    """Main system coordinator"""
    
    def __init__(self):
        self.message_queue = MessageQueue()
        self.supervisor = SupervisorAgent(self.message_queue)
        self.agents: Dict[str, BaseAgent] = {
            'supervisor': self.supervisor
        }
        
        print("🚀 Multi-Agent System initialized")
    

    def register_agent(self, agent: BaseAgent):
        """Register a new agent with the system"""
        self.agents[agent.name] = agent
        self.supervisor.register_agent(agent.name, agent.role)
        print(f"✅ Agent {agent.name} registered")
    

    def start_all_agents(self):
        """Start all registered agents"""
        print("\n▶️ Starting all agents...")
        for agent in self.agents.values():
            agent.start()
            time.sleep(0.1)  # Stagger starts
        print("✅ All agents started\n")
    
    
    def stop_all_agents(self):
        """Stop all agents gracefully"""
        print("\n⏸️ Stopping all agents...")
        for agent in self.agents.values():
            agent.stop()
        print("✅ All agents stopped\n")

    
    def submit_task(self, task_type: str, data: Dict[str, Any]) -> str:
        """Submit a task to the system"""
        
        # Send to supervisor
        message = Message(
            sender="user",
            recipient="supervisor",
            message_type=MessageType.REQUEST,
            content={
                'task_type': task_type,
                'data': data
            },
            priority=Priority.HIGH
        )
        
        self.message_queue.send(message)
        
        # Generate task ID (supervisor will create proper one)
        task_id = f"task_{int(time.time()*1000)}"
        print(f"📤 Task submitted: {task_type}")
        
        return task_id
    

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'agents': {name: agent.get_status() for name, agent in self.agents.items()},
            'message_queue_size': sum(q.qsize() for q in self.message_queue.queues.values()),
            'active_tasks': len(self.supervisor.active_tasks),
            'completed_tasks': len(self.supervisor.completed_tasks)
        }
    
    def get_message_history(self, limit: int = 20) -> List[Dict]:
        """Get recent message history"""
        messages = self.message_queue.get_history(limit)
        return [msg.to_dict() for msg in messages]


# ==================== DEMO & TESTING ====================

def demo_phase1():
    """Demonstrate Phase 1 functionality"""
    
    print("="*60)
    print("🤖 MULTI-AGENT SYSTEM - PHASE 1 DEMO")
    print("="*60)
    print()
    
    # Initialize system
    system = MultiAgentSystem()
    
    # Start agents
    system.start_all_agents()
    
    # Wait for agents to be ready
    time.sleep(1)
    
    # Submit test task
    print("\n" + "="*60)
    print("📝 Submitting test task...")
    print("="*60)
    
    task_id = system.submit_task(
        task_type='analyze_paper',
        data={
            'paper_title': 'Attention Is All You Need',
            'paper_url': 'https://arxiv.org/abs/1706.03762'
        }
    )
    
    # Give time for processing
    time.sleep(2)
    
    # Check system status
    print("\n" + "="*60)
    print("📊 System Status:")
    print("="*60)
    status = system.get_system_status()
    print(json.dumps(status, indent=2))
    
    # Check message history
    print("\n" + "="*60)
    print("📜 Message History:")
    print("="*60)
    history = system.get_message_history(10)
    for msg in history:
        print(f"{msg['sender']:12} → {msg['recipient']:12} : {msg['type']:10} @ {msg['timestamp']}")
    
    # Stop system
    print("\n" + "="*60)
    print("Stopping system...")
    print("="*60)
    system.stop_all_agents()
    
    time.sleep(1)
    
    print("\n✅ Phase 1 Demo Complete!")
    print("\nNext: Phase 2 will add Analyst and Evaluator agents")


if __name__ == "__main__":
    demo_phase1()