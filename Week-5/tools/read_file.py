"""
ReadFile Tool - Read internal documentation
"""

from pathlib import Path
from langchain_core.tools import tool

WEEK5_DIR = Path(__file__).parent.parent
IT_DOCS_PATH = WEEK5_DIR / "data" / "it_docs"
FINANCE_DOCS_PATH = WEEK5_DIR / "data" / "finance_docs"


def search_docs(docs_path: Path, query: str) -> str:
    """Search documents in a directory for relevant content."""
    if not docs_path.exists():
        return f"Documentation directory not found: {docs_path}"

    query_lower = query.lower()
    keywords = [kw.strip() for kw in query_lower.split() if len(kw.strip()) > 2]

    results = []

    for file_path in docs_path.glob("*.txt"):
        content = file_path.read_text(encoding="utf-8")
        content_lower = content.lower()

        # Check keyword matches
        match_count = sum(content_lower.count(kw) for kw in keywords)

        if match_count > 0:
            results.append({
                "file": file_path.name,
                "content": content,
                "relevance": match_count,
            })

    # Sort by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)

    if not results:
        return f"No relevant documents found for: {query}"

    # Return top results
    formatted = f"**Documentation Search Results for: '{query}'**\n\n"
    for r in results[:2]:  # Top 2 most relevant docs
        formatted += f"### {r['file']}\n"
        formatted += f"{r['content']}\n\n"
        formatted += "---\n\n"

    return formatted


@tool
def read_it_docs(query: str) -> str:
    """
    Search and read internal IT documentation.

    Use this tool to find information about:
    - VPN setup and configuration
    - Approved software list
    - Laptop and hardware requests
    - IT policies and procedures
    - Technical support guides

    Args:
        query: Search query for IT documentation

    Returns:
        Relevant IT documentation content
    """
    return search_docs(IT_DOCS_PATH, query)


@tool
def read_finance_docs(query: str) -> str:
    """
    Search and read internal Finance documentation.

    Use this tool to find information about:
    - Expense reimbursement process
    - Budget reports and access
    - Payroll schedule and information
    - Finance policies and procedures

    Args:
        query: Search query for Finance documentation

    Returns:
        Relevant Finance documentation content
    """
    return search_docs(FINANCE_DOCS_PATH, query)
