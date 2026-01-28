"""
Web Search Tool for Industry Benchmarks, Trends, and Regulatory Updates
Uses DuckDuckGo for web searches - no API key required
"""

from langchain_core.tools import tool
from ddgs import DDGS


@tool
def web_search(query: str) -> str:
    """
    Search the web for industry benchmarks, trends, and regulatory updates.

    Use this tool to fetch:
    - Industry benchmarks and statistics
    - Technology trends and market analysis
    - Regulatory updates and compliance news
    - Competitor information and market research

    Args:
        query: Search query string (e.g., "IT services hiring trends 2024")

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


@tool
def search_industry_benchmarks(query: str) -> str:
    """
    Search for industry benchmarks and statistics.

    Use this for queries about:
    - Hiring metrics and trends
    - Market size and growth rates
    - Performance benchmarks
    - Industry averages and comparisons

    Args:
        query: Topic to search for (e.g., "IT services employee turnover rate")

    Returns:
        Industry benchmark data and statistics
    """
    enhanced_query = f"{query} industry benchmark statistics 2024 2025"
    return web_search.invoke(enhanced_query)


@tool
def search_trends(query: str) -> str:
    """
    Search for industry trends and market analysis.

    Use this for queries about:
    - Technology trends
    - Market forecasts
    - Emerging technologies
    - Industry predictions

    Args:
        query: Topic to search for (e.g., "cloud computing trends")

    Returns:
        Trend analysis and market insights
    """
    enhanced_query = f"{query} trends market analysis forecast 2024 2025"
    return web_search.invoke(enhanced_query)


@tool
def search_regulatory_updates(query: str) -> str:
    """
    Search for regulatory updates and compliance news.

    Use this for queries about:
    - New regulations and laws
    - Compliance requirements
    - Policy changes
    - Government guidelines

    Args:
        query: Topic to search for (e.g., "AI regulation GDPR")

    Returns:
        Regulatory updates and compliance information
    """
    enhanced_query = f"{query} regulation compliance law update 2024 2025"
    return web_search.invoke(enhanced_query)


def get_web_search_tools():
    """Return all web search tools for use with LangChain agent."""
    return [
        web_search,
        search_industry_benchmarks,
        search_trends,
        search_regulatory_updates,
    ]
