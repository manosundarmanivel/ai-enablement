"""
Tools for the support agent
"""

from langchain_core.tools import tool
from ddgs import DDGS


@tool
def web_search(query: str) -> str:
    """Search the web for information using DuckDuckGo.

    Args:
        query: The search query string

    Returns:
        Search results as formatted text
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return "No search results found."

        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"{i}. {r.get('title', 'No title')}")
            formatted.append(f"   {r.get('body', 'No description')}")
            formatted.append(f"   URL: {r.get('href', 'No URL')}")
            formatted.append("")

        return "\n".join(formatted)

    except Exception as e:
        return f"Search error: {str(e)}"


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2", "10 * 5")

    Returns:
        The result of the calculation
    """
    try:
        # Safe evaluation of mathematical expressions
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression. Only numbers and basic operators allowed."

        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"


@tool
def get_current_time() -> str:
    """Get the current date and time.

    Returns:
        Current date and time as a formatted string
    """
    from datetime import datetime

    now = datetime.now()
    return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


@tool
def company_policy(topic: str) -> str:
    """Look up company policies on various topics.

    Args:
        topic: The policy topic to look up (e.g., "vacation", "remote work", "expenses")

    Returns:
        Information about the company policy
    """
    policies = {
        "vacation": """
VACATION POLICY:
- Full-time employees: 15 days PTO per year
- After 3 years: 20 days PTO
- After 5 years: 25 days PTO
- Unused PTO carries over (max 5 days)
- Request via HR Portal at least 2 weeks in advance
""",
        "remote work": """
REMOTE WORK POLICY:
- Hybrid model: 3 days office, 2 days remote
- Core hours: 10 AM - 4 PM local time
- VPN required for remote access
- Equipment provided: laptop, monitor, keyboard
- Home office stipend: $500 one-time
""",
        "expenses": """
EXPENSE POLICY:
- Submit within 30 days of expense
- Receipts required for amounts > $25
- Pre-approval needed for expenses > $500
- Reimbursement within 2 weeks
- Categories: Travel, Meals, Software, Equipment
""",
        "sick leave": """
SICK LEAVE POLICY:
- 10 sick days per year
- No carryover
- Doctor's note required for 3+ consecutive days
- Can be used for self or family care
- Report absence by 9 AM
""",
    }

    topic_lower = topic.lower()
    for key, value in policies.items():
        if key in topic_lower or topic_lower in key:
            return value

    return f"No policy found for '{topic}'. Available topics: vacation, remote work, expenses, sick leave"
