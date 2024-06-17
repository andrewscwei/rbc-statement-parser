import argparse
import os
import re
import sys
from datetime import datetime
from typing import Dict, List

from app.entities import Transaction
from app.utils import ccy_to_float, file_to_str, str_to_date
from parse_config import parse_config
from utils import str_to_file

REGEX_SHORT_DATE = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) \d{2}"
REGEX_LONG_DATE = (
    r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)) (\d{2})(?:, )?(\d{4})?"
)
REGEX_AMOUNT = r"-?\$[\d,]+\.\d{2}"
REGEX_CODE = r"\d{23}"
OUTPUT_ROW_FORMAT = "{date}\t\t\t{code}\t{description}\t{category}\t{amount}"

file_out = f"out.txt"

month_map = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="A script that parses RBC chequing and VISA statements in PDF format and extracts transactions"
    )

    parser.add_argument("path", type=str, help="Path or to PDF or directory of PDFs")
    files = []

    args = parser.parse_args()

    if os.path.isdir(args.path):
        files = [
            os.path.abspath(os.path.join(args.path, f))
            for f in os.listdir(args.path)
            if f.lower().endswith(".pdf")
        ]
    elif os.path.isfile(args.path) and args.path.lower().endswith(".pdf"):
        files = [os.path.abspath(args.path)]

    if len(files) == 0:
        print("No valid PDF files found in the specified directory.")
        sys.exit(1)

    return files


def extract_start_date(raw: str) -> datetime | None:
    regex = rf"statement from ({REGEX_LONG_DATE}) to ({REGEX_LONG_DATE})"

    if match := re.search(regex, raw, re.IGNORECASE):
        end_year = match[8]
        start_month = match[2]
        start_day = match[3]
        start_year = match[4] or end_year

        return str_to_date(f"{start_month} {start_day} {start_year}")

    return None


def get_category(description: str, lookup: Dict[str, List[str]] = None) -> str:
    if lookup is None:
        lookup = {}

    for category in lookup:
        for regex in lookup[category]:
            if re.match(regex, description, re.IGNORECASE):
                return category

    return None


def should_exclude(description: str, lookup: List[str]) -> bool:
    for regex in lookup:
        if re.match(regex, description, re.IGNORECASE):
            return True

    return False


def format_tx(tx: Transaction, with_padding: bool = False) -> str:
    date = tx["date"].strftime("%Y-%m-%d")
    code = tx["code"] or ""
    description = tx["description"]
    amount = f"{tx['amount']:.2f}"
    category = tx["category"]

    return OUTPUT_ROW_FORMAT.format(
        date=date if not with_padding else date.ljust(10),
        code=code if not with_padding else code.ljust(23),
        description=description if not with_padding else description.ljust(90),
        amount=amount if not with_padding else amount.ljust(10),
        category=category if not with_padding else category.ljust(30),
    )


def parse_tx(line: str, start_date: datetime, config: dict) -> Transaction | None:
    regex = (
        rf"^({REGEX_SHORT_DATE})\s+?({REGEX_SHORT_DATE})\s+?(.*)\s+?({REGEX_AMOUNT})"
    )

    if (match := re.match(regex, line, re.IGNORECASE)) is None:
        return None

    date = match[1]
    posting_date = match[2]
    body = match[3]
    code = res.group(0) if (res := re.search(REGEX_CODE, body, re.IGNORECASE)) else None
    description = body.replace(f" {code}", "") if code else body
    amount = match[4]
    category = get_category(description, config["categories"]) or "Other"

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

    return None if should_exclude(description, config["excludes"]) else tx


def parse_pdf(file: str, config: dict) -> List[Transaction]:
    raw = file_to_str(file)
    start_date = extract_start_date(raw)
    txs = []
    lines = re.sub(
        rf"\n(?!{REGEX_SHORT_DATE}\n{REGEX_SHORT_DATE})", " ", raw, 0, re.IGNORECASE
    )

    for line in lines.split("\n"):
        if match := re.match(
            rf"^{REGEX_SHORT_DATE}.*?{REGEX_AMOUNT}", line, re.IGNORECASE
        ):
            if tx := parse_tx(match[0], start_date, config):
                txs.append(tx)

    return txs


def main():
    config = parse_config()
    files = parse_args()
    txs = []
    write_str = ""

    for file in files:
        txs.extend(parse_pdf(file, config))

    txs = sorted(txs, key=lambda tx: tx["date"])

    for tx in txs:
        write_str += format_tx(tx, True) + "\n"

    str_to_file(write_str, file_out)

    print(write_str)
    print()
    print(f'Parsing files > "{file_out}"... OK: {len(txs)} entr(ies) in result')


if __name__ == "__main__":
    main()
