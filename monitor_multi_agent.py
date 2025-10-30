"""
Multi-Agent System - Real-Time Monitoring Dashboard
Live visualization of agent activity and message flow
"""

import time
from datetime import datetime
from demo_phase1 import MultiAgentSystem, MessageType, Priority
import json


class SystemMonitor:
    """Real-time monitoring and visualization"""
    
    def __init__(self, system: MultiAgentSystem):
        self.system = system
        self.start_time = datetime.now()
    
    def clear_screen(self):
        """Clear terminal (cross-platform)"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def format_uptime(self) -> str:
        """Format system uptime"""
        elapsed = datetime.now() - self.start_time
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def draw_header(self):
        """Draw monitor header"""
        print("=" * 80)
        print("🤖 MULTI-AGENT SYSTEM - REAL-TIME MONITOR".center(80))
        print(f"Uptime: {self.format_uptime()}".center(80))
        print("=" * 80)
        print()

    
    def draw_agent_status(self):
        """Draw agent status table"""
        print("📊 AGENT STATUS")
        print("-" * 80)
        
        # Header
        print(f"{'Agent':<20} {'State':<12} {'Messages':<10} {'Errors':<8} {'Alive':<8}")
        print("-" * 80)
        
        # Agents
        for name, agent in self.system.agents.items():
            status = agent.get_status()
            
            # Color code state
            state = status['state']
            if state == 'idle':
                state_display = f"🟢 {state}"
            elif state == 'processing':
                state_display = f"🟡 {state}"
            elif state == 'error':
                state_display = f"🔴 {state}"
            else:
                state_display = f"⚪ {state}"
            
            alive = "✅" if status['is_alive'] else "❌"
            
            print(f"{name:<20} {state_display:<20} {status['messages_processed']:<10} "
                  f"{status['error_count']:<8} {alive:<8}")
        
        print()

    
    def draw_task_queue(self):
        """Draw active tasks"""
        print("📋 ACTIVE TASKS")
        print("-" * 80)
        
        active_tasks = self.system.supervisor.get_all_tasks()
        
        if not active_tasks:
            print("No active tasks")
        else:
            for task_id, task in list(active_tasks.items())[:5]:  # Show top 5
                task_type = task.get('task_type', 'unknown')
                status = task.get('status', 'unknown')
                assigned = len(task.get('assigned_agents', []))
                responses = len(task.get('responses_received', {}))
                
                print(f"  [{task_id}] {task_type:<20} Status: {status:<10} "
                      f"Agents: {assigned} Responses: {responses}")
        
        print()


    def draw_message_flow(self):
        """Draw recent message activity"""
        print("📨 MESSAGE FLOW (Last 10)")
        print("-" * 80)
        
        history = self.system.get_message_history(limit=10)
        
        if not history:
            print("No messages yet")
        else:
            for msg in reversed(history):  # Most recent first
                timestamp = msg['timestamp'].split('T')[1].split('.')[0]  # Just time
                sender = msg['sender'][:12]
                recipient = msg['recipient'][:12]
                msg_type = msg['type']
                
                # Icon for message type
                if msg_type == 'request':
                    icon = "📤"
                elif msg_type == 'response':
                    icon = "📥"
                elif msg_type == 'error':
                    icon = "⚠️"
                else:
                    icon = "📨"
                
                print(f"  {timestamp} {icon} {sender:<12} → {recipient:<12} : {msg_type}")
        
        print()
    
    def draw_system_metrics(self):
        """Draw system-wide metrics"""
        print("📈 SYSTEM METRICS")
        print("-" * 80)
        
        status = self.system.get_system_status()
        
        total_agents = len(status['agents'])
        active_agents = sum(1 for a in status['agents'].values() if a['is_alive'])
        queue_size = status['message_queue_size']
        active_tasks = status['active_tasks']
        completed_tasks = status['completed_tasks']
        
        # Calculate total messages processed
        total_messages = sum(a['messages_processed'] for a in status['agents'].values())
        total_errors = sum(a['error_count'] for a in status['agents'].values())
        
        print(f"  Agents: {active_agents}/{total_agents} active")
        print(f"  Message Queue: {queue_size} pending")
        print(f"  Tasks: {active_tasks} active, {completed_tasks} completed")
        print(f"  Messages Processed: {total_messages}")
        print(f"  Errors: {total_errors}")
        print()
    

    def draw_footer(self):
        """Draw footer with controls"""
        print("=" * 80)
        print("Press Ctrl+C to stop monitoring".center(80))
        print("=" * 80)
    

    def display(self):
        """Display full monitor view"""
        self.clear_screen()
        self.draw_header()
        self.draw_agent_status()
        self.draw_task_queue()
        self.draw_message_flow()
        self.draw_system_metrics()
        self.draw_footer()
    
    def run(self, refresh_rate: float = 1.0):
        """Run monitoring loop"""
        try:
            while True:
                self.display()
                time.sleep(refresh_rate)
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")

def demo_monitor():
    """Demonstrate the monitoring dashboard"""
    
    print("🚀 Starting Multi-Agent System with Monitor...")
    print()
    
    # Create and start system
    system = MultiAgentSystem()
    system.start_all_agents()
    
    # Wait for agents to be ready
    time.sleep(1)
    
    # Submit some test tasks
    print("📤 Submitting test tasks...")
    for i in range(3):
        system.submit_task(
            task_type=f'test_task_{i}',
            data={'index': i, 'description': f'Test task number {i}'}
        )
        time.sleep(0.5)
    
    print()
    print("▶️ Starting real-time monitor...")
    print("   (Monitor will update every second)")
    print()
    time.sleep(2)


     
    # Create and run monitor
    monitor = SystemMonitor(system)
    
    try:
        monitor.run(refresh_rate=1.0)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n🛑 Stopping system...")
        system.stop_all_agents()
        time.sleep(1)
        print("✅ System stopped cleanly")


# ==================== INTERACTIVE DEMO ====================

def interactive_demo():
    """Interactive demo with user commands"""
    
    print("="*60)
    print("🤖 MULTI-AGENT SYSTEM - INTERACTIVE DEMO")
    print("="*60)
    print()
    
    # Initialize system
    system = MultiAgentSystem()
    system.start_all_agents()
    time.sleep(1)

    print("✅ System started!")
    print()
    print("Available commands:")
    print("  task <type>    - Submit a task")
    print("  status         - Show system status")
    print("  messages       - Show message history")
    print("  agents         - Show agent details")
    print("  monitor        - Start live monitor")
    print("  help           - Show this help")
    print("  quit           - Stop system and exit")
    print()
    

    try:
        while True:
            cmd = input(">>> ").strip().lower()
            
            if cmd.startswith('task'):
                parts = cmd.split()
                task_type = parts[1] if len(parts) > 1 else 'generic_task'
                
                task_id = system.submit_task(
                    task_type=task_type,
                    data={'user_input': cmd}
                )
                print(f"✅ Task submitted: {task_id}")
                print()
            
            elif cmd == 'status':
                status = system.get_system_status()
                print("\n📊 System Status:")
                print(json.dumps(status, indent=2))
                print()
            
            elif cmd == 'messages':
                history = system.get_message_history(20)
                print("\n📨 Recent Messages:")
                for msg in history[-10:]:  # Last 10
                    print(f"  {msg['sender']:12} → {msg['recipient']:12} : {msg['type']}")
                print()
            
            elif cmd == 'agents':
                print("\n🤖 Agent Details:")
                for name, agent in system.agents.items():
                    status = agent.get_status()
                    print(f"\n  {name}:")
                    print(f"    Role: {status['role']}")
                    print(f"    State: {status['state']}")
                    print(f"    Messages: {status['messages_processed']}")
                    print(f"    Errors: {status['error_count']}")
                print()
            
            elif cmd == 'monitor':
                print("\n▶️ Starting live monitor (Ctrl+C to stop)...")
                time.sleep(1)
                monitor = SystemMonitor(system)
                try:
                    monitor.run(refresh_rate=1.0)
                except KeyboardInterrupt:
                    print("\n✅ Monitor stopped")
                    print()
            
            elif cmd == 'help':
                print("\nAvailable commands:")
                print("  task <type>    - Submit a task")
                print("  status         - Show system status")
                print("  messages       - Show message history")
                print("  agents         - Show agent details")
                print("  monitor        - Start live monitor")
                print("  help           - Show this help")
                print("  quit           - Stop system and exit")
                print()
            
            elif cmd == 'quit':
                print("\n🛑 Shutting down...")
                break
            
            else:
                print(f"❌ Unknown command: {cmd}")
                print("   Type 'help' for available commands")
                print()
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted")
    
    finally:
        print("Stopping agents...")
        system.stop_all_agents()
        time.sleep(1)
        print("✅ System stopped cleanly")
        print("Goodbye! 👋")

# ==================== STRESS TEST ====================

def stress_test():
    """Stress test the system with high load"""
    
    print("="*60)
    print("🔥 MULTI-AGENT SYSTEM - STRESS TEST")
    print("="*60)
    print()
    
    system = MultiAgentSystem()

     # Add multiple dummy agents
    from demo_phase1 import BaseAgent, Message, MessageType
    
    class StressTestAgent(BaseAgent):
        def process(self, message):
            # Simulate work
            time.sleep(0.01)
            return {'processed': True}
     # Create 5 test agents
    for i in range(5):
        agent = StressTestAgent(
            f"stress_agent_{i}",
            "Stress Test Agent",
            system.message_queue
        )
        system.register_agent(agent)
    
    print(f"✅ Created {len(system.agents)} agents")
    
    # Start system
    system.start_all_agents()
    time.sleep(1)
    
    print("▶️ System started")
    print()


     # Submit many tasks
    num_tasks = 100
    print(f"📤 Submitting {num_tasks} tasks...")
    
    start_time = time.time()
    
    for i in range(num_tasks):
        system.submit_task(
            task_type='stress_test',
            data={'task_number': i}
        )
        
        if (i + 1) % 20 == 0:
            print(f"   Submitted {i + 1}/{num_tasks} tasks...")
    
    submit_duration = time.time() - start_time
    
    print(f"\n✅ All tasks submitted in {submit_duration:.2f}s")
    print(f"   Rate: {num_tasks/submit_duration:.0f} tasks/sec")
    print()

    
     # Let system process
    print("⏳ Processing tasks...")
    time.sleep(5)
    
    # Show results
    print("\n📊 Stress Test Results:")
    status = system.get_system_status()
    
    total_messages = sum(a['messages_processed'] for a in status['agents'].values())
    total_errors = sum(a['error_count'] for a in status['agents'].values())
    
    print(f"  Total messages processed: {total_messages}")
    print(f"  Total errors: {total_errors}")
    print(f"  Active tasks remaining: {status['active_tasks']}")
    print(f"  Completed tasks: {status['completed_tasks']}")
    print()
    
    if total_errors == 0:
        print("✅ STRESS TEST PASSED - No errors!")
    else:
        print(f"⚠️ STRESS TEST WARNING - {total_errors} errors occurred")
    
    # Cleanup
    print("\n🛑 Stopping system...")
    system.stop_all_agents()
    time.sleep(1)
    print("✅ Done")


# ==================== MAIN MENU ====================

def main_menu():
    """Main menu for choosing demos"""
    
    print("="*60)
    print("🤖 MULTI-AGENT SYSTEM - PHASE 1 DEMOS")
    print("="*60)
    print()
    print("Choose a demo:")
    print()
    print("  1. Basic Demo           - Simple task submission")
    print("  2. Live Monitor         - Real-time system monitoring")
    print("  3. Interactive Demo     - Command-line interface")
    print("  4. Stress Test          - High-load performance test")
    print("  5. Run Tests            - Execute test suite")
    print("  6. Exit")
    print()
    
    while True:
        choice = input("Enter choice (1-6): ").strip()
        print()
        
        if choice == '1':
            from demo_phase1 import demo_phase1
            demo_phase1()
            break
        
        elif choice == '2':
            demo_monitor()
            break
        
        elif choice == '3':
            interactive_demo()
            break
        
        elif choice == '4':
            stress_test()
            break
        
        elif choice == '5':
            print("Running test suite...\n")
            # Import and run tests
            try:
                from test_multi_agent import run_tests
                run_tests()
            except ImportError:
                print("❌ Test file not found. Make sure test_multi_agent.py exists.")
            break
        
        elif choice == '6':
            print("Goodbye! 👋")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-6.")
            print()


if __name__ == "__main__":
    main_menu()
