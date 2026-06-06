from datetime import datetime
from typing import Dict, List, Optional, TypedDict


class Config(TypedDict, total=False):
    format: Optional[str]
    """Optional string format for outputting transactions.

    Uses placeholders for transaction fields, including: `{date}`, `{method}`,
    `{code}`, `{description}`, `{category}`, `{amount}`, and `{posting_date}`.
    """

    categories: Optional[Dict[str, List[str]]]
    """A mapping of category names to lists of regex patterns for matching
    transaction descriptions.
    """

    excludes: Optional[List[str]]
    """A list of regex patterns for matching transaction descriptions that
    should be excluded.
    """


class Transaction(TypedDict, total=False):
    date: datetime
    """The date of the transaction."""

    method: str
    """The method of the transaction (e.g., "visa")."""

    description: str
    """The description of the transaction."""

    amount: float
    """The amount of the transaction."""

    category: Optional[str]
    """The category of the transaction (if matched)."""

    code: Optional[str]
    """The code extracted from the transaction description (if any)."""

    posting_date: datetime
    """The posting date of the transaction."""
