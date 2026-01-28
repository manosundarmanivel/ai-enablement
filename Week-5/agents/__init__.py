"""
Multi-Agent Support System Agents

- SupervisorAgent: Routes queries to IT or Finance
- ITAgent: Handles IT-related queries
- FinanceAgent: Handles Finance-related queries
"""

from .supervisor import SupervisorAgent
from .it_agent import ITAgent
from .finance_agent import FinanceAgent

__all__ = [
    "SupervisorAgent",
    "ITAgent",
    "FinanceAgent",
]
