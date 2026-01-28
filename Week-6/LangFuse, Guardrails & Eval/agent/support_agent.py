"""
Support Agent with LangFuse tracing integration
"""

from langchain_aws import ChatBedrock
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime
import time

from config import DEFAULT_MODEL
from agent.tools import web_search, calculator, get_current_time, company_policy
from agent.tracing import LangFuseTracer


SUPPORT_SYSTEM_PROMPT = """You are a helpful support agent for a company.

Your role is to assist employees with various questions and tasks.

## Your Tools

1. **web_search** - Search the web for general information
2. **calculator** - Perform mathematical calculations
3. **get_current_time** - Get the current date and time
4. **company_policy** - Look up company policies

## Guidelines

1. Always be helpful and professional
2. Use tools when appropriate to provide accurate information
3. For company-specific questions, check company_policy first
4. For general information, use web_search
5. Be concise but thorough in your responses

## Response Format

- Start with a direct answer
- Provide relevant details
- Offer to help with follow-up questions
"""


class SupportAgent:
    """Support Agent with LangFuse tracing for observability."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.1,
        enable_tracing: bool = True,
        session_id: str = None,
    ):
        """Initialize the support agent.

        Args:
            model: Bedrock model ID
            temperature: Model temperature
            enable_tracing: Whether to enable LangFuse tracing
            session_id: Optional session ID for tracing
        """
        self.model = model
        self.enable_tracing = enable_tracing
        self.session_id = session_id or f"support-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Initialize LLM
        self.llm = ChatBedrock(
            model_id=model,
            model_kwargs={"temperature": temperature},
        )

        # Initialize tools
        self.tools = [web_search, calculator, get_current_time, company_policy]

        # Create the agent
        self.agent = create_react_agent(
            self.llm,
            self.tools,
            prompt=SUPPORT_SYSTEM_PROMPT,
        )

        # Initialize tracing
        if enable_tracing:
            self.tracer = LangFuseTracer(session_id=self.session_id)
        else:
            self.tracer = None

        # Chat history
        self.chat_history = []

        # Metrics tracking
        self.metrics = {
            "total_queries": 0,
            "total_tool_calls": 0,
            "tools_used": {},
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_latency_ms": 0,
        }

    def query(self, question: str, user_id: str = None) -> dict:
        """Process a query with full tracing.

        Args:
            question: User's question
            user_id: Optional user identifier for tracing

        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()
        self.metrics["total_queries"] += 1

        # Prepare messages
        messages = self.chat_history + [HumanMessage(content=question)]

        # Start trace for this query
        trace_span = None
        if self.enable_tracing and self.tracer:
            trace_span = self.tracer.start_trace(
                name="support_agent_query",
                user_id=user_id,
                input_data=question,
                metadata={
                    "query_number": self.metrics["total_queries"],
                    "model": self.model,
                },
            )

        try:
            tools_used = []
            final_response = ""
            input_tokens = 0
            output_tokens = 0

            # Stream the agent response
            for event in self.agent.stream({"messages": messages}):
                if "agent" in event:
                    for msg in event["agent"].get("messages", []):
                        # Track tool calls
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tc in msg.tool_calls:
                                tool_name = tc.get("name", "unknown")
                                if tool_name not in tools_used:
                                    tools_used.append(tool_name)
                                    self.metrics["total_tool_calls"] += 1
                                    self.metrics["tools_used"][tool_name] = (
                                        self.metrics["tools_used"].get(tool_name, 0) + 1
                                    )
                                    print(f"    -> Using tool: {tool_name}")

                                    # Log tool usage
                                    if self.tracer:
                                        self.tracer.log_tool_call(
                                            tool_name=tool_name,
                                            tool_input=tc.get("args", {}),
                                        )

                        # Get final response
                        if hasattr(msg, "content") and msg.content:
                            if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                final_response = msg.content

                        # Track token usage if available
                        if hasattr(msg, "usage_metadata") and msg.usage_metadata:
                            input_tokens += msg.usage_metadata.get("input_tokens", 0)
                            output_tokens += msg.usage_metadata.get("output_tokens", 0)

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            self.metrics["total_latency_ms"] += latency_ms
            self.metrics["total_input_tokens"] += input_tokens
            self.metrics["total_output_tokens"] += output_tokens

            # Update chat history
            self.chat_history.append(HumanMessage(content=question))
            self.chat_history.append(AIMessage(content=final_response))

            # Log generation and end trace
            if self.tracer:
                self.tracer.log_generation(
                    name="llm_response",
                    model=self.model,
                    prompt=question,
                    completion=final_response,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    metadata={"tools_used": tools_used},
                )
                self.tracer.end_span(
                    trace_span,
                    output_data=final_response,
                    metadata={
                        "latency_ms": latency_ms,
                        "tools_used": tools_used,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                    },
                )
                self.tracer.flush()

            return {
                "response": final_response,
                "tools_used": tools_used,
                "latency_ms": latency_ms,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            if self.tracer and trace_span:
                self.tracer.end_span(
                    trace_span,
                    output_data=f"Error: {str(e)}",
                    metadata={"error": str(e), "latency_ms": latency_ms},
                )
                self.tracer.flush()
            return {
                "response": f"Error: {str(e)}",
                "tools_used": [],
                "latency_ms": latency_ms,
                "error": str(e),
            }

    def get_metrics(self) -> dict:
        """Get current metrics.

        Returns:
            Dictionary with metrics
        """
        avg_latency = (
            self.metrics["total_latency_ms"] / self.metrics["total_queries"]
            if self.metrics["total_queries"] > 0
            else 0
        )

        return {
            **self.metrics,
            "average_latency_ms": round(avg_latency, 2),
            "session_id": self.session_id,
        }

    def clear_history(self):
        """Clear conversation history."""
        self.chat_history = []

    def shutdown(self):
        """Shutdown the agent and flush traces."""
        if self.tracer:
            self.tracer.shutdown()
