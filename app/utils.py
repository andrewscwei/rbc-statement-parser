import re
from datetime import datetime
from typing import Dict, List

import fitz

from .entities import Transaction


def str_to_date(string: str):
    return datetime.strptime(string, "%b %d %Y")


def ccy_to_float(ccy: str):
    return float(ccy.replace("$", "").replace(",", ""))


def file_to_str(file_path: str) -> str:
    if file_path.lower().endswith(".pdf"):
        document = fitz.open(file_path)
        string = ""

        for page_num in range(len(document)):
            page = document.load_page(page_num)
            string += page.get_text("text")

        return string

    with open(file_path, "r", encoding="utf8") as file:
        string = file.read()

    return string


def str_to_file(string: str, file_path: str):
    with open(file_path, "w", encoding="utf8") as file:
        file.write(string)


def format_tx(
    tx: Transaction,
    format_str: str = "{date}\t{code}\t{description}\t{category}\t{amount}",
    with_padding: bool = False,
) -> str:
    date = tx["date"].strftime("%Y-%m-%d")
    code = tx["code"] or ""
    description = tx["description"]
    amount = f"{tx['amount']:.2f}"
    category = tx["category"]

    return format_str.format(
        date=date if not with_padding else date.ljust(10),
        code=code if not with_padding else code.ljust(23),
        description=description if not with_padding else description.ljust(90),
        amount=amount if not with_padding else amount.ljust(10),
        category=category if not with_padding else category.ljust(30),
    )


def match_category(description: str, lookup: Dict[str, List[str]] = None) -> str | None:
    if lookup is None:
        lookup = {}

    for category in lookup:
        for regex in lookup[category]:
            if re.match(regex, description, re.IGNORECASE):
                return category

    return None


def should_exclude(description: str, lookup: List[str] = None) -> bool:
    if lookup is None:
        lookup = []

    for regex in lookup:
        if re.match(regex, description, re.IGNORECASE):
            return True

    return False
