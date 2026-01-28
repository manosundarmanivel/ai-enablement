"""
NeMo Guardrails integration for the Support Agent

This module provides GuardedSupportAgent - Full NeMo Guardrails integration with AWS Bedrock
"""

import asyncio
import time
from pathlib import Path
from datetime import datetime

from nemoguardrails import RailsConfig, LLMRails
from nemoguardrails.actions import action
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage

from config import DEFAULT_MODEL
from agent.tools import web_search, calculator, get_current_time, company_policy
from agent.tracing import LangFuseTracer


# Path to guardrails configuration
GUARDRAILS_CONFIG_PATH = Path(__file__).parent


class GuardedSupportAgent:
    """Support Agent with full NeMo Guardrails for input/output validation.

    Uses NeMo Guardrails with:
    - Input rails: Validate and filter user input
    - Output rails: Validate and filter bot responses
    - Custom actions: Connect to tools (calculator, time, policy, etc.)
    - Conversation flows: Define allowed conversation patterns
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.1,
        session_id: str = None,
    ):
        """Initialize the guarded support agent.

        Args:
            model: Bedrock model ID
            temperature: Model temperature
            session_id: Optional session identifier
        """
        self.model = model
        self.temperature = temperature
        self.session_id = session_id or f"guarded-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Initialize the base LLM for actions and guardrails
        self.llm = ChatBedrock(
            model_id=model,
            model_kwargs={"temperature": temperature},
        )

        # Chat history
        self.chat_history = []

        # Guardrail metrics (must be initialized before _register_actions)
        self.metrics = {
            "total_queries": 0,
            "blocked_inputs": 0,
            "blocked_outputs": 0,
            "passed_queries": 0,
            "total_latency_ms": 0,
            "actions_executed": {},
        }

        # Initialize LangFuse tracing
        self.tracer = LangFuseTracer(session_id=self.session_id)
        if self.tracer.enabled:
            print(f"LangFuse tracing enabled for session: {self.session_id}")
        else:
            print("LangFuse tracing disabled (missing credentials)")

        # Load guardrails configuration
        print(f"Loading NeMo Guardrails from: {GUARDRAILS_CONFIG_PATH}")
        self.config = RailsConfig.from_path(str(GUARDRAILS_CONFIG_PATH))

        # Initialize the rails with the ChatBedrock LLM passed directly
        self.rails = LLMRails(
            config=self.config,
            llm=self.llm,
        )

        # Register custom actions
        self._register_actions()

    def _register_actions(self):
        """Register custom actions with the guardrails."""
        # Store reference for closure
        llm = self.llm
        metrics = self.metrics
        tracer = self.tracer

        @action(name="web_search_action")
        async def web_search_action(query: str) -> str:
            """Search the web for information."""
            metrics["actions_executed"]["web_search"] = metrics["actions_executed"].get("web_search", 0) + 1
            try:
                result = web_search.invoke(query)
                tracer.log_tool_call("web_search", query, result)
                return result
            except Exception as e:
                return f"Search error: {str(e)}"

        @action(name="calculator_action")
        async def calculator_action(expression: str) -> str:
            """Perform mathematical calculations."""
            metrics["actions_executed"]["calculator"] = metrics["actions_executed"].get("calculator", 0) + 1
            try:
                result = calculator.invoke(expression)
                tracer.log_tool_call("calculator", expression, result)
                return result
            except Exception as e:
                return f"Calculation error: {str(e)}"

        @action(name="get_time_action")
        async def get_time_action() -> str:
            """Get the current date and time."""
            metrics["actions_executed"]["get_time"] = metrics["actions_executed"].get("get_time", 0) + 1
            try:
                result = get_current_time.invoke({})
                tracer.log_tool_call("get_time", {}, result)
                return result
            except Exception as e:
                return f"Time error: {str(e)}"

        @action(name="company_policy_action")
        async def company_policy_action(topic: str) -> str:
            """Look up company policies."""
            metrics["actions_executed"]["company_policy"] = metrics["actions_executed"].get("company_policy", 0) + 1
            try:
                result = company_policy.invoke(topic)
                tracer.log_tool_call("company_policy", topic, result)
                return result
            except Exception as e:
                return f"Policy lookup error: {str(e)}"

        @action(name="general_query")
        async def general_query(user_input: str = None) -> str:
            """Handle general queries using the LLM."""
            metrics["actions_executed"]["general_query"] = metrics["actions_executed"].get("general_query", 0) + 1
            if not user_input:
                return "I'm not sure what you're asking. Could you please clarify?"

            try:
                messages = [HumanMessage(content=user_input)]
                response = llm.invoke(messages)
                tracer.log_tool_call("general_query", user_input, response.content)
                return response.content
            except Exception as e:
                return f"Error processing query: {str(e)}"

        # Register all actions with the rails
        self.rails.register_action(web_search_action, "web_search_action")
        self.rails.register_action(calculator_action, "calculator_action")
        self.rails.register_action(get_time_action, "get_time_action")
        self.rails.register_action(company_policy_action, "company_policy_action")
        self.rails.register_action(general_query, "general_query")

    async def query_async(self, question: str) -> dict:
        """Process a query with guardrails (async).

        Args:
            question: User's question

        Returns:
            Dictionary with response and guardrail metadata
        """
        start_time = time.time()
        self.metrics["total_queries"] += 1

        # Start LangFuse trace
        span = self.tracer.start_trace(
            name="guardrails_query",
            input_data=question,
            metadata={"model": self.model, "query_number": self.metrics["total_queries"]}
        )

        try:
            # Prepare messages including history
            messages = self.chat_history + [{"role": "user", "content": question}]

            # Generate response with guardrails
            response = await self.rails.generate_async(messages=messages)

            latency_ms = int((time.time() - start_time) * 1000)
            self.metrics["total_latency_ms"] += latency_ms

            # Extract content from response
            content = ""
            if isinstance(response, dict):
                content = response.get("content", "")
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)

            # Check if input was blocked (common blocked responses)
            blocked_phrases = [
                "I'm sorry, but I can't help with that",
                "I cannot assist with",
                "goes against our company policies",
                "I cannot share personal information",
            ]

            was_blocked = any(phrase in content for phrase in blocked_phrases)

            if was_blocked:
                self.metrics["blocked_inputs"] += 1
                # Log blocked query to LangFuse
                self.tracer.end_span(span, output_data=content, metadata={
                    "blocked": True,
                    "block_type": "input_rail",
                    "latency_ms": latency_ms
                })
                self.tracer.log_event("query_blocked", metadata={"question": question, "response": content})
                self.tracer.flush()
                return {
                    "response": content,
                    "blocked": True,
                    "block_type": "input_rail",
                    "latency_ms": latency_ms,
                }

            self.metrics["passed_queries"] += 1

            # Update chat history
            self.chat_history.append({"role": "user", "content": question})
            self.chat_history.append({"role": "assistant", "content": content})

            # Log successful query to LangFuse
            self.tracer.end_span(span, output_data=content, metadata={
                "blocked": False,
                "latency_ms": latency_ms,
                "actions_executed": dict(self.metrics["actions_executed"])
            })

            # Log generation for token tracking
            self.tracer.log_generation(
                name="guardrails_response",
                model=self.model,
                prompt=question,
                completion=content,
                metadata={"latency_ms": latency_ms}
            )
            self.tracer.flush()

            return {
                "response": content,
                "blocked": False,
                "latency_ms": latency_ms,
                "actions_executed": dict(self.metrics["actions_executed"]),
            }

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            # Log error to LangFuse
            self.tracer.end_span(span, output_data=str(e), metadata={
                "error": True,
                "latency_ms": latency_ms
            })
            self.tracer.flush()
            return {
                "response": f"Error: {str(e)}",
                "blocked": False,
                "error": str(e),
                "latency_ms": latency_ms,
            }

    def query(self, question: str) -> dict:
        """Process a query with guardrails (sync wrapper).

        Args:
            question: User's question

        Returns:
            Dictionary with response and guardrail metadata
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If there's already a running loop, use nest_asyncio
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(self.query_async(question))
            else:
                return asyncio.run(self.query_async(question))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self.query_async(question))

    def get_metrics(self) -> dict:
        """Get guardrail metrics.

        Returns:
            Dictionary with metrics
        """
        total = self.metrics["total_queries"]
        blocked = self.metrics["blocked_inputs"] + self.metrics["blocked_outputs"]

        block_rate = (blocked / total * 100) if total > 0 else 0
        avg_latency = (self.metrics["total_latency_ms"] / total) if total > 0 else 0

        return {
            **self.metrics,
            "block_rate_percent": round(block_rate, 2),
            "average_latency_ms": round(avg_latency, 2),
            "session_id": self.session_id,
        }

    def clear_history(self):
        """Clear conversation history."""
        self.chat_history = []

    def get_info(self) -> dict:
        """Get information about the guardrails configuration."""
        return {
            "model": self.model,
            "config_path": str(GUARDRAILS_CONFIG_PATH),
            "session_id": self.session_id,
            "registered_actions": [
                "web_search_action",
                "calculator_action",
                "get_time_action",
                "company_policy_action",
                "general_query",
            ],
        }


# Export classes
__all__ = ["GuardedSupportAgent"]
