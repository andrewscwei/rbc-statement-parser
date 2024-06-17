import re
from datetime import datetime
from typing import List, Optional

from .entities import Transaction
from .utils import match_category, parse_float, read_pdf, should_exclude

PAT_FILE_PATH = r"visa statement"
PAT_MONTH = r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
PAT_DAY = r"\d{1,2}"
PAT_YEAR = r"\d{4}"
PAT_DATE_SHORT = rf"(?:{PAT_MONTH}) {PAT_DAY}"
PAT_DATE_LONG = rf"((?:{PAT_MONTH})) ({PAT_DAY})(?:, )?({PAT_YEAR})?"
PAT_AMOUNT = r"-?\$[\d,]+\.\d{2}"
PAT_CODE = r"\d{23}"


def is_visa(file_path: str) -> bool:
    return bool(re.search(PAT_FILE_PATH, file_path, re.IGNORECASE))


def extract_start_date(pdf: str) -> Optional[datetime]:
    regex = rf"statement from ({PAT_DATE_LONG}) to ({PAT_DATE_LONG})"

    if match := re.search(regex, pdf, re.IGNORECASE):
        end_year = match[8]
        start_month = match[2]
        start_day = match[3]
        start_year = match[4] or end_year

        return parse_date(f"{start_month} {start_day} {start_year}")

    return None


def parse_date(string: str) -> datetime:
    return datetime.strptime(string, "%b %d %Y")


def parse_transaction(
    line: str,
    start_date: datetime,
    categories: dict,
    excludes: list,
) -> Optional[Transaction]:
    pat = rf"^({PAT_DATE_SHORT})\s+?({PAT_DATE_SHORT})\s+?(.*?)\s+?({PAT_AMOUNT})"

    if (match := re.match(pat, line, re.IGNORECASE)) is None:
        return None

    date, posting_date, body, amount = match.groups()
    code = res.group(0) if (res := re.search(PAT_CODE, body, re.IGNORECASE)) else None
    description = body.replace(f" {code}", "") if code else body

    if should_exclude(description, lookup=excludes):
        return None

    category = match_category(description, lookup=categories) or "Other"
    ref_date = parse_date(f"{date} {start_date.year}")
    ref_year = start_date.year + (1 if ref_date.month < start_date.month else 0)

    return {
        "amount": parse_float(amount) * -1,
        "method": "visa",
        "category": category,
        "code": code,
        "date": parse_date(f"{date} {ref_year}"),
        "description": description,
        "posting_date": parse_date(f"{posting_date} {ref_year}"),
    }


def parse_visa(
    pdf_path: str,
    categories: Optional[dict],
    excludes: Optional[list],
) -> List[Transaction]:
    pdf = read_pdf(pdf_path)
    start_date = extract_start_date(pdf)

    lines = re.sub(
        rf"\n(?!{PAT_DATE_SHORT}\n{PAT_DATE_SHORT})",
        " ",
        pdf,
        flags=re.IGNORECASE,
    )

    transactions = [
        tx
        for line in lines.splitlines()
        if (tx := parse_transaction(line, start_date, categories or {}, excludes or []))
    ]

    return transactions
