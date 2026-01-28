"""
Presidio Internal Research Agent Tools

1. RAG Tool - Search HR Policy documents (FAISS + Gemini embeddings)
2. MCP Tool - Search Google Docs for insurance via MCP protocol
3. Web Search Tool - Fetch industry benchmarks and trends (DuckDuckGo)
"""

from .rag_tool import search_hr_policies, get_rag_tools, vectorize_documents
from .mcp_tool import search_insurance_docs, get_mcp_tools
from .web_search_tool import web_search, get_web_search_tools


def get_all_tools():
    """Return all tools for the Presidio Research Agent."""
    return [
        search_hr_policies,
        search_insurance_docs,
        web_search,
    ]


__all__ = [
    "search_hr_policies",
    "get_rag_tools",
    "vectorize_documents",
    "search_insurance_docs",
    "get_mcp_tools",
    "web_search",
    "get_web_search_tools",
    "get_all_tools",
]
