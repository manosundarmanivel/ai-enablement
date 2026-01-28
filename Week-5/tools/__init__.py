"""
Multi-Agent Support System Tools

Tools available for IT and Finance agents:
- read_file: Read internal documentation
- web_search: Search external sources
"""

from .read_file import read_it_docs, read_finance_docs
from .web_search import web_search

__all__ = [
    "read_it_docs",
    "read_finance_docs",
    "web_search",
]
