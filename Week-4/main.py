#!/usr/bin/env python3
"""
Presidio Internal Research Agent - Main Application
Interactive CLI for the research agent with three tools.
"""

import os
import sys
from dotenv import load_dotenv

from agent import create_agent
from tools import vectorize_documents


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           PRESIDIO INTERNAL RESEARCH AGENT                       ║
║                                                                  ║
║   Tools: RAG (HR Policies) | MCP (Insurance) | Web Search        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")


def print_help():
    print("""
COMMANDS:
  /help       - Show this help
  /tools      - List available tools
  /examples   - Show example queries
  /clear      - Clear conversation history
  /vectorize  - Re-vectorize HR policy documents
  /quit       - Exit

EXAMPLE QUERIES:
  • "Summarize all customer feedback related to our Q1 marketing campaigns."
  • "Compare our current hiring trend with industry benchmarks."
  • "Find relevant compliance policies related to AI data handling."
  • "What is our professional liability coverage?"
""")


def print_examples():
    print("""
EXAMPLE QUERIES BY TOOL:

RAG TOOL (HR Policies):
  • "What is the PTO policy for employees?"
  • "Summarize customer feedback from Q1 marketing campaigns"
  • "What are the current hiring metrics?"
  • "What training budget is available?"

MCP TOOL (Insurance - Google Docs):
  • "What is our professional liability coverage limit?"
  • "How do I file an insurance claim?"
  • "What does our cyber insurance cover?"

WEB SEARCH (Industry Data):
  • "IT services industry hiring trends 2024"
  • "AI regulation updates in the US"
  • "Cloud migration market benchmarks"

COMBINED QUERIES:
  • "Compare our hiring metrics with industry benchmarks"
  • "Find AI compliance policies and relevant regulations"
""")


def print_tools(agent):
    print("\nAVAILABLE TOOLS:")
    print("-" * 50)
    for name, desc in agent.get_tools_info().items():
        print(f"\n🔧 {name}")
        # Print first 200 chars of description
        print(f"   {desc[:200]}...")


def main():
    load_dotenv()

    # Check AWS credentials
    if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
        print("Error: AWS credentials not set!")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env file")
        sys.exit(1)

    print_banner()

    # Initialize agent
    print("🔄 Initializing agent...")
    try:
        agent = create_agent(verbose=False)
        print("Agent ready!\n")
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
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
                elif cmd == "/tools":
                    print_tools(agent)
                elif cmd == "/examples":
                    print_examples()
                elif cmd == "/clear":
                    agent.clear_history()
                    print("Conversation history cleared.")
                elif cmd == "/vectorize":
                    print("Vectorizing documents...")
                    vectorize_documents()
                    print("Done!")
                else:
                    print(f" Unknown command: {cmd}")
                    print("  Type /help for available commands.")
                continue

            # Process query
            print("\nSearching...\n")
            response = agent.query(user_input)
            print(f"Agent: {response}")
            print("\n" + "-" * 60)

        except KeyboardInterrupt:
            print("\n\nType /quit to exit.")
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
