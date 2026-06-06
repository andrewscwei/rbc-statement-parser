import re
from typing import Optional


def parse_currency(s: str) -> float:
    """Convert a currency string like "$1,234.56" to a float."""

    return float(s.replace("$", "").replace(",", ""))


def match_category(description: str, categories: dict) -> Optional[str]:
    """Match a transaction description to a category based on regex patterns."""

    for category in categories:
        for regex in categories[category]:
            if re.search(regex, description, re.IGNORECASE):
                return category

    return None


def should_exclude(description: str, exclude_patterns: list) -> bool:
    """Determine if a transaction should be excluded based on its description
    and a list of regex patterns.
    """

    for regex in exclude_patterns:
        if re.match(regex, description, re.IGNORECASE):
            return True

    return False
