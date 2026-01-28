#!/usr/bin/env python3
"""
Multi-Agent Support System - Main Application

A supervisor agent routes queries to IT or Finance specialist agents.
"""

import os
import sys
from dotenv import load_dotenv

from agents import SupervisorAgent, ITAgent, FinanceAgent


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           PRESIDIO MULTI-AGENT SUPPORT SYSTEM                    ║
║                                                                  ║
║   Supervisor → Routes to IT Agent or Finance Agent               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")


def print_help():
    print("""
COMMANDS:
  /help       - Show this help
  /examples   - Show example queries
  /clear      - Clear conversation history
  /quit       - Exit

EXAMPLE QUERIES:

IT Questions:
  • "How do I set up VPN?"
  • "What software is approved for use?"
  • "How to request a new laptop?"

Finance Questions:
  • "How do I file a reimbursement?"
  • "Where can I find last month's budget report?"
  • "When is payroll processed?"
""")


def print_examples():
    print("""
EXAMPLE QUERIES BY DEPARTMENT:

IT AGENT:
  • "How do I set up VPN?"
  • "What software is approved for use?"
  • "How to request a new laptop?"
  • "My email isn't working"
  • "What are the laptop specs for developers?"

FINANCE AGENT:
  • "How do I file a reimbursement?"
  • "Where can I find last month's budget report?"
  • "When is payroll processed?"
  • "What's the daily meal allowance?"
  • "How do I access my pay stub?"
""")


class MultiAgentSystem:
    """Orchestrates the multi-agent support system."""

    def __init__(self):
        print("  Loading Supervisor Agent...")
        self.supervisor = SupervisorAgent()

        print("  Loading IT Agent...")
        self.it_agent = ITAgent()

        print("  Loading Finance Agent...")
        self.finance_agent = FinanceAgent()

    def process_query(self, query: str) -> str:
        """Process a user query through the multi-agent system."""
        # Step 1: Supervisor classifies the query
        department, reasoning = self.supervisor.route(query)
        print(f"\n  [Supervisor] → Routing to {department} Agent")

        # Step 2: Route to appropriate agent
        if department == "IT":
            response = self.it_agent.query(query)
        else:
            response = self.finance_agent.query(query)

        return response

    def clear_history(self):
        """Clear all agent histories."""
        self.it_agent.clear_history()
        self.finance_agent.clear_history()


def main():
    load_dotenv()

    # Check AWS credentials
    if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
        print("Error: AWS credentials not set!")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env file")
        sys.exit(1)

    print_banner()

    # Initialize multi-agent system
    print("Initializing Multi-Agent System...")
    try:
        system = MultiAgentSystem()
        print("System ready!\n")
    except Exception as e:
        print(f"Failed to initialize: {e}")
        sys.exit(1)

    print("Type /help for commands or ask a question.\n")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                cmd = user_input.lower()

                if cmd in ["/quit", "/exit", "/q"]:
                    print("\nGoodbye!")
                    break
                elif cmd == "/help":
                    print_help()
                elif cmd == "/examples":
                    print_examples()
                elif cmd == "/clear":
                    system.clear_history()
                    print("Conversation history cleared.")
                else:
                    print(f"Unknown command: {cmd}")
                    print("Type /help for available commands.")
                continue

            # Process query through multi-agent system
            response = system.process_query(user_input)
            print(f"\nAgent: {response}")
            print("\n" + "-" * 60)

        except KeyboardInterrupt:
            print("\n\nType /quit to exit.")
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
