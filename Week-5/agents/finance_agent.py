"""
Finance Agent - Handles all Finance-related queries
"""

from langchain_aws import ChatBedrock
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage

from tools.read_file import read_finance_docs
from tools.web_search import web_search


FINANCE_SYSTEM_PROMPT = """You are a Finance Support Agent for Presidio.

Your role is to help employees with finance-related questions.

## Your Tools

1. **read_finance_docs** - Search internal Finance documentation for:
   - Expense reimbursement process
   - Budget reports and access
   - Payroll schedule and information
   - Finance policies

2. **web_search** - Search the web for:
   - Tax regulations
   - Financial best practices
   - Public finance information

## Guidelines

1. ALWAYS use read_finance_docs first to check internal documentation
2. Use web_search for general finance info not in internal docs
3. Be accurate with numbers, dates, and deadlines
4. Include relevant contact info (Finance team, email, phone)
5. For sensitive matters, direct them to appropriate contacts

## Response Format

- Start with a direct answer
- Provide step-by-step instructions when applicable
- Include specific dates, amounts, and deadlines
- Include contact information for further help
- Be concise but thorough
"""


class FinanceAgent:
    """Finance Support Agent with document and web search tools."""

    def __init__(
        self,
        model: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        temperature: float = 0.1,
    ):
        self.llm = ChatBedrock(
            model_id=model,
            model_kwargs={"temperature": temperature},
        )
        self.tools = [read_finance_docs, web_search]
        self.chat_history = []

        self.agent = create_react_agent(
            self.llm,
            self.tools,
            prompt=FINANCE_SYSTEM_PROMPT,
        )

    def query(self, question: str) -> str:
        """Process a Finance-related query."""
        try:
            messages = self.chat_history + [HumanMessage(content=question)]

            tools_used = []
            final_response = ""

            for event in self.agent.stream({"messages": messages}):
                if "agent" in event:
                    for msg in event["agent"].get("messages", []):
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tc in msg.tool_calls:
                                tool_name = tc.get("name", "unknown")
                                if tool_name not in tools_used:
                                    tools_used.append(tool_name)
                                    print(f"    → Finance Agent using: {tool_name}")

                        if hasattr(msg, "content") and msg.content:
                            if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                final_response = msg.content

            self.chat_history.append(HumanMessage(content=question))
            self.chat_history.append(AIMessage(content=final_response))

            return final_response

        except Exception as e:
            return f"Finance Agent Error: {str(e)}"

    def clear_history(self):
        """Clear conversation history."""
        self.chat_history = []
