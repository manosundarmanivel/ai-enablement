"""
Presidio Internal Research Agent
A LangChain agent with three tools for comprehensive internal research.
"""

from langchain_aws import ChatBedrock
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage

from tools import get_all_tools

SYSTEM_PROMPT = """You are an intelligent Internal Research Agent for Presidio, a leading IT solutions provider.

Your role is to deliver accurate, contextual, and actionable responses to employee queries.

## Your Tools

1. **search_hr_policies** - Search internal HR documents:
   - Customer feedback reports (Q1 marketing campaigns, etc.)
   - Hiring policies and recruitment metrics
   - AI and data handling compliance policies
   - Employee handbook (PTO, benefits, training budgets)

2. **search_insurance_docs** - Search Google Docs for insurance:
   - Professional liability coverage and limits
   - Cyber insurance details
   - Health insurance benefits
   - Claims processes

3. **web_search** - Search external industry data:
   - Industry benchmarks and statistics
   - Hiring trends and market analysis
   - Regulatory updates and compliance news

## Tool Selection Rules

ALWAYS use tools to answer questions. Analyze the query and select the right tool(s):

| Query Type | Tool to Use |
|------------|-------------|
| Customer feedback, Q1 campaigns | search_hr_policies |
| Hiring metrics, recruitment data | search_hr_policies |
| AI compliance, data handling policies | search_hr_policies |
| PTO, benefits, training budget | search_hr_policies |
| Insurance coverage, liability, claims | search_insurance_docs |
| Industry benchmarks, market trends | web_search |
| Regulatory updates, external compliance | web_search |

## For Comparison Queries

When asked to "compare" internal data with industry benchmarks:
1. FIRST use search_hr_policies to get Presidio's internal data
2. THEN use web_search to get industry benchmarks
3. Synthesize both results into a comparison

Example: "Compare our hiring trend with industry benchmarks"
→ Step 1: search_hr_policies("hiring metrics recruitment data")
→ Step 2: web_search("IT services industry hiring trends 2024")
→ Step 3: Compare and summarize findings

## Response Format

Structure your response clearly:
- **Summary**: Brief answer to the question
- **Details**: Key findings with specific numbers/facts
- **Sources**: Which documents/searches provided the information
- **Recommendations**: Actionable next steps if applicable

Be thorough but concise. Always cite where the information came from.
"""


class PresidioResearchAgent:
    """Internal Research Agent for Presidio employees."""

    def __init__(
        self,
        model: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        temperature: float = 0.1,
        verbose: bool = False,
    ):
        self.llm = ChatBedrock(
            model_id=model,
            model_kwargs={"temperature": temperature},
        )
        self.tools = get_all_tools()
        self.verbose = verbose
        self.chat_history = []

        # Create react agent with LangGraph
        self.agent = create_react_agent(
            self.llm,
            self.tools,
            prompt=SYSTEM_PROMPT,
        )

    def query(self, question: str) -> str:
        """Query the agent with a question."""
        try:
            messages = self.chat_history + [HumanMessage(content=question)]

            # Stream to show tool usage in real-time
            tools_used = []
            final_response = ""

            for event in self.agent.stream({"messages": messages}):
                # Check for tool calls in agent messages
                if "agent" in event:
                    for msg in event["agent"].get("messages", []):
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tc in msg.tool_calls:
                                tool_name = tc.get("name", "unknown")
                                if tool_name not in tools_used:
                                    tools_used.append(tool_name)
                                    print(f"  → Using: {tool_name}")

                        # Capture final response (message without tool_calls)
                        if hasattr(msg, "content") and msg.content:
                            if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                final_response = msg.content

            # Update chat history
            self.chat_history.append(HumanMessage(content=question))
            self.chat_history.append(AIMessage(content=final_response))

            return final_response

        except Exception as e:
            return f"Error: {str(e)}"

    def clear_history(self):
        """Clear conversation history."""
        self.chat_history = []

    def get_tools_info(self):
        """Get information about available tools."""
        return {tool.name: tool.description for tool in self.tools}


def create_agent(verbose: bool = False) -> PresidioResearchAgent:
    """Create and return a Presidio Research Agent."""
    return PresidioResearchAgent(verbose=verbose)
