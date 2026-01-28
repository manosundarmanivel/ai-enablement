"""
MCP Client - Connects to MCP server for insurance document search
Wraps MCP protocol as a LangChain tool
"""

import asyncio
import sys
from pathlib import Path
from langchain_core.tools import tool

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = Path(__file__).parent / "server.py"


class MCPInsuranceClient:
    """Client that connects to the MCP insurance server."""

    def __init__(self):
        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(SERVER_PATH)],
            cwd=str(SERVER_PATH.parent),
        )

    async def search(self, query: str) -> str:
        """Search insurance documents via MCP server."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    "search_insurance_docs",
                    arguments={"query": query}
                )

                if result.content:
                    return result.content[0].text

                return "No results found."


def _run_async(coro):
    """Run async function in sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


_client = MCPInsuranceClient()


@tool
def search_insurance_docs(query: str) -> str:
    """
    Search Presidio's insurance documents via MCP server.

    This tool connects to an MCP server that searches Google Docs for:
    - Insurance policy coverage and limits
    - Professional liability (E&O) insurance details
    - Cyber liability insurance information
    - General liability coverage
    - Health insurance benefits
    - Claims processes and procedures

    Args:
        query: Search query about insurance policies or coverage

    Returns:
        Relevant insurance policy information from Google Docs
    """
    try:
        result = _run_async(_client.search(query))
        return result
    except Exception as e:
        return f"MCP Error: {str(e)}"


def get_mcp_tools():
    """Return MCP tools for LangChain agent."""
    return [search_insurance_docs]
