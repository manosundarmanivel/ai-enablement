"""
Supervisor Agent - Routes queries to IT or Finance agents
"""

from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage


CLASSIFICATION_PROMPT = """You are a query classifier for a company support system.

Your job is to classify user queries into one of two categories:
- IT: Technical issues, software, hardware, VPN, laptops, systems access
- FINANCE: Money matters, expenses, reimbursements, payroll, budgets, reports

Analyze the query and respond with ONLY one word: either "IT" or "FINANCE"

Examples:
- "How do I set up VPN?" → IT
- "How to file a reimbursement?" → FINANCE
- "What software is approved?" → IT
- "When is payroll processed?" → FINANCE
- "I need a new laptop" → IT
- "Where's the budget report?" → FINANCE
- "My email isn't working" → IT
- "How do I submit expenses?" → FINANCE

Respond with only: IT or FINANCE"""


class SupervisorAgent:
    """Supervisor that classifies and routes queries."""

    def __init__(self, model: str = "anthropic.claude-3-haiku-20240307-v1:0"):
        self.llm = ChatBedrock(
            model_id=model,
            model_kwargs={"temperature": 0},
        )

    def classify(self, query: str) -> str:
        """Classify a query as IT or FINANCE."""
        messages = [
            SystemMessage(content=CLASSIFICATION_PROMPT),
            HumanMessage(content=f"Classify this query: {query}"),
        ]

        response = self.llm.invoke(messages)
        classification = response.content.strip().upper()

        # Ensure valid classification
        if "IT" in classification:
            return "IT"
        elif "FINANCE" in classification:
            return "FINANCE"
        else:
            # Default to IT for technical-sounding queries
            return "IT"

    def route(self, query: str) -> tuple[str, str]:
        """Route a query and return (department, reasoning)."""
        classification = self.classify(query)

        if classification == "IT":
            reasoning = "This query is related to technical/IT matters."
        else:
            reasoning = "This query is related to finance/money matters."

        return classification, reasoning
