"""
WebSearch Tool - Search external sources
"""

from langchain_core.tools import tool
from ddgs import DDGS


@tool
def web_search(query: str) -> str:
    """
    Search the web for external information.

    Use this tool to find:
    - Public documentation and guides
    - Industry best practices
    - Current regulations and compliance info
    - General knowledge not in internal docs

    Args:
        query: Search query string

    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return f"No results found for: {query}"

        formatted = f"**Web Search Results for: '{query}'**\n\n"

        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            url = r.get("href", "")
            snippet = r.get("body", "")

            formatted += f"### {i}. {title}\n"
            formatted += f"**URL:** {url}\n"
            formatted += f"{snippet}\n\n"

        return formatted

    except Exception as e:
        return f"Search error: {str(e)}"
