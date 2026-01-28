"""
MCP Tool - Insurance document search via Model Context Protocol

The MCP server (server.py) connects to Google Docs.
The client (insurance_tool.py) wraps it as a LangChain tool.
"""

from .insurance_tool import search_insurance_docs, get_mcp_tools

__all__ = ["search_insurance_docs", "get_mcp_tools"]
