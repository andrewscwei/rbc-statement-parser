import re
from typing import Optional


def parse_float(s: str):
    return float(s.replace("$", "").replace(",", ""))


def match_category(description: str, categories: dict) -> Optional[str]:
    for category in categories:
        for regex in categories[category]:
            if re.search(regex, description, re.IGNORECASE):
                return category

    return None


def should_exclude(description: str, exclude_patterns: list) -> bool:
    for regex in exclude_patterns:
        if re.match(regex, description, re.IGNORECASE):
            return True

    return False
