import os
import re
from typing import Optional

import fitz

from .entities import Transaction


def parse_float(string: str):
    return float(string.replace("$", "").replace(",", ""))


def read_pdf(pdf_path: str, html: bool = False) -> str:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File {pdf_path} not found")

    if not pdf_path.lower().endswith(".pdf"):
        raise TypeError(f"File {pdf_path} is not a recognized PDF")

    document = fitz.open(pdf_path)
    string = ""

    for page_num in range(len(document)):
        page = document.load_page(page_num)
        string += page.get_text("html" if html else "text")

    return string


def read_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")

    with open(file_path, "r", encoding="utf8") as file:
        string = file.read()

    return string


def write_file(string: str, file_path: str):
    with open(file_path, "w", encoding="utf8") as file:
        file.write(string)


def match_category(description: str, lookup: dict) -> Optional[str]:
    for category in lookup:
        for regex in lookup[category]:
            if re.search(regex, description, re.IGNORECASE):
                return category

    return None


def should_exclude(description: str, lookup: list) -> bool:
    for regex in lookup:
        if re.match(regex, description, re.IGNORECASE):
            return True

    return False


def format_transaction(
    tx: Transaction,
    template: str = "{date}\t{method}\t{code}\t{description}\t{category}\t{amount}",
    default_category: str = "",
    padding: bool = False,
) -> str:
    amount = f"{tx.get('amount'):.2f}"
    method = tx.get("method")
    category = tx.get("category") or default_category
    code = tx.get("code") or ""
    date = tx.get("date").strftime("%Y-%m-%d")
    description = tx.get("description")
    posting_date = tx.get("posting_date").strftime("%Y-%m-%d")

    return template.format(
        amount=amount if not padding else amount.ljust(10),
        method=method if not padding else method.ljust(10),
        category=category if not padding else category.ljust(30),
        code=code if not padding else code.ljust(23),
        date=date if not padding else date.ljust(10),
        description=description if not padding else description.ljust(90),
        posting_date=posting_date if not padding else posting_date.ljust(10),
    )
