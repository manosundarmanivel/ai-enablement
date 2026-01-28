"""
LangFuse tracing integration for observability (v3.x API)
"""

import os
from datetime import datetime

from langfuse import Langfuse

from config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST


# Set environment variables for LangFuse auto-instrumentation
if LANGFUSE_PUBLIC_KEY:
    os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
if LANGFUSE_SECRET_KEY:
    os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY
if LANGFUSE_HOST:
    os.environ["LANGFUSE_HOST"] = LANGFUSE_HOST


class LangFuseTracer:
    """LangFuse tracing wrapper for LangChain agents (v3.x API)."""

    def __init__(self, session_id: str = None):
        """Initialize LangFuse tracer.

        Args:
            session_id: Optional session ID for grouping traces
        """
        self.session_id = session_id or f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.enabled = bool(LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY)

        if self.enabled:
            try:
                self.langfuse = Langfuse(
                    public_key=LANGFUSE_PUBLIC_KEY,
                    secret_key=LANGFUSE_SECRET_KEY,
                    host=LANGFUSE_HOST,
                )
            except Exception as e:
                print(f"Warning: Failed to initialize LangFuse: {e}")
                self.enabled = False
                self.langfuse = None
        else:
            self.langfuse = None

    def start_trace(self, name: str, user_id: str = None, input_data: str = None, metadata: dict = None):
        """Start a new trace span.

        Args:
            name: Name of the trace
            user_id: Optional user identifier
            input_data: Optional input data
            metadata: Optional metadata

        Returns:
            Span object or None if tracing disabled
        """
        if not self.enabled or not self.langfuse:
            return None

        try:
            span = self.langfuse.start_span(
                name=name,
                input=input_data,
                metadata={
                    **(metadata or {}),
                    "session_id": self.session_id,
                    "user_id": user_id,
                },
            )
            return span
        except Exception as e:
            print(f"Warning: Failed to start trace: {e}")
            return None

    def end_span(self, span, output_data=None, metadata: dict = None):
        """End a span with output data.

        Args:
            span: The span object to end
            output_data: Output data
            metadata: Additional metadata
        """
        if span is None:
            return

        try:
            # First update with output and metadata, then end
            span.update(
                output=output_data,
                metadata=metadata,
            )
            span.end()
        except Exception as e:
            print(f"Warning: Failed to end span: {e}")

    def log_generation(
        self,
        name: str,
        model: str,
        prompt: str,
        completion: str,
        input_tokens: int = None,
        output_tokens: int = None,
        metadata: dict = None,
    ):
        """Log a generation (LLM call) to LangFuse.

        Args:
            name: Name of the generation
            model: Model identifier
            prompt: Input prompt
            completion: Model output
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            metadata: Additional metadata
        """
        if not self.enabled or not self.langfuse:
            return

        try:
            gen = self.langfuse.start_generation(
                name=name,
                model=model,
                input=prompt,
                metadata={
                    **(metadata or {}),
                    "session_id": self.session_id,
                },
            )
            # Update with output and usage, then end
            usage_details = None
            if input_tokens or output_tokens:
                usage_details = {
                    "input": input_tokens or 0,
                    "output": output_tokens or 0,
                    "total": (input_tokens or 0) + (output_tokens or 0),
                }
            gen.update(
                output=completion,
                usage_details=usage_details,
            )
            gen.end()
        except Exception as e:
            print(f"Warning: Failed to log generation: {e}")

    def log_tool_call(self, tool_name: str, tool_input, tool_output=None):
        """Log a tool call to LangFuse.

        Args:
            tool_name: Name of the tool
            tool_input: Tool input
            tool_output: Tool output
        """
        if not self.enabled or not self.langfuse:
            return

        try:
            span = self.langfuse.start_span(
                name=f"tool:{tool_name}",
                input=tool_input,
                metadata={"session_id": self.session_id, "tool_name": tool_name},
            )
            if tool_output:
                span.update(output=tool_output)
            span.end()
        except Exception as e:
            print(f"Warning: Failed to log tool call: {e}")

    def log_event(self, name: str, metadata: dict = None):
        """Log an event to LangFuse.

        Args:
            name: Event name
            metadata: Event metadata
        """
        if not self.enabled or not self.langfuse:
            return

        try:
            self.langfuse.create_event(
                name=name,
                metadata={
                    **(metadata or {}),
                    "session_id": self.session_id,
                },
            )
        except Exception as e:
            print(f"Warning: Failed to log event: {e}")

    def flush(self):
        """Flush all pending traces to LangFuse."""
        if self.langfuse:
            try:
                self.langfuse.flush()
            except Exception:
                pass

    def shutdown(self):
        """Shutdown the LangFuse client."""
        if self.langfuse:
            try:
                self.langfuse.flush()
                self.langfuse.shutdown()
            except Exception:
                pass


# Export
__all__ = ["LangFuseTracer"]
