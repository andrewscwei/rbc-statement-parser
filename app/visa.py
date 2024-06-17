import re
from datetime import datetime
from typing import Dict, List

from .entities import Transaction
from .utils import (
    ccy_to_float,
    file_to_str,
    match_category,
    should_exclude,
    str_to_date,
)

REGEX_DATE_SHORT = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) \d{2}"
REGEX_DATE_LONG = (
    r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)) (\d{2})(?:, )?(\d{4})?"
)
REGEX_AMOUNT = r"-?\$[\d,]+\.\d{2}"
REGEX_CODE = r"\d{23}"


def get_start_date(pdf: str) -> datetime | None:
    regex = rf"statement from ({REGEX_DATE_LONG}) to ({REGEX_DATE_LONG})"

    if match := re.search(regex, pdf, re.IGNORECASE):
        end_year = match[8]
        start_month = match[2]
        start_day = match[3]
        start_year = match[4] or end_year

        return str_to_date(f"{start_month} {start_day} {start_year}")

    return None


def parse_tx(
    line: str,
    start_date: datetime,
    categories: Dict[str, List[str]] = None,
    excludes: List[str] = None,
) -> Transaction | None:
    if (
        match := re.match(
            rf"^({REGEX_DATE_SHORT})\s+?({REGEX_DATE_SHORT})\s+?(.*)\s+?({REGEX_AMOUNT})",
            line,
            re.IGNORECASE,
        )
    ) is None:
        return None

    date = match[1]
    posting_date = match[2]
    body = match[3]
    code = res.group(0) if (res := re.search(REGEX_CODE, body, re.IGNORECASE)) else None
    description = body.replace(f" {code}", "") if code else body
    amount = match[4]
    category = match_category(description, categories) or "Other"

    tmp_year = start_date.year
    tmp_date = str_to_date(f"{date} {start_date.year}")

    if tmp_date.month < start_date.month:
        tmp_year += 1

    tx: Transaction = {
        "amount": ccy_to_float(amount),
        "category": category,
        "code": code,
        "date": str_to_date(f"{date} {tmp_year}"),
        "description": description,
        "posting_date": str_to_date(f"{posting_date} {tmp_year}"),
    }

    if should_exclude(description, excludes):
        return None

    return tx


def parse_visa(
    file_path: str,
    categories: Dict[str, List[str]] = None,
    excludes: List[str] = None,
) -> List[Transaction]:
    raw = file_to_str(file_path)
    start_date = get_start_date(raw)
    transactions = []
    lines = re.sub(
        rf"\n(?!{REGEX_DATE_SHORT}\n{REGEX_DATE_SHORT})", " ", raw, 0, re.IGNORECASE
    )

    for line in lines.split("\n"):
        if match := re.match(
            rf"^{REGEX_DATE_SHORT}.*?{REGEX_AMOUNT}", line, re.IGNORECASE
        ):
            if tx := parse_tx(match[0], start_date, categories, excludes):
                transactions.append(tx)

    return transactions
