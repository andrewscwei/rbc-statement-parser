import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List

from app.entities import Transaction
from app.utils import ccy_to_float, file_to_str, format_tx, str_to_date
from utils import str_to_file

REGEX_DATE_SHORT = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) \d{2}"
REGEX_DATE_LONG = (
    r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)) (\d{2})(?:, )?(\d{4})?"
)
REGEX_AMOUNT = r"-?\$[\d,]+\.\d{2}"
REGEX_CODE = r"\d{23}"
OUTPUT_ROW_FORMAT = "{date}\t\t\t{code}\t{description}\t{category}\t{amount}"


def parse_config(path: str) -> dict:
    config = {}

    try:
        with open(path, encoding="utf8") as json_file:
            data = json.load(json_file)

            try:
                config["categories"] = data["categories"]
            except Exception as exc:
                print(exc)

            try:
                config["excludes"] = data["excludes"]
            except Exception as exc:
                print(exc)
    except Exception as exc:
        pass

    return config


def parse_files(path: str) -> List[str]:
    files = []

    if os.path.isdir(path):
        files = [
            os.path.abspath(os.path.join(path, f))
            for f in os.listdir(path)
            if f.lower().endswith(".pdf")
        ]
    elif os.path.isfile(path) and path.lower().endswith(".pdf"):
        files = [os.path.abspath(path)]

    return files


def parse_args() -> tuple[List[str], dict, str]:
    parser = argparse.ArgumentParser(
        description="A script that parses RBC chequing and VISA statements in PDF format and extracts transactions"
    )

    parser.add_argument("path", help="Path or to PDF or directory of PDFs")
    parser.add_argument(
        "--config", "-c", help="Path to config file", default="config.json"
    )
    parser.add_argument("--out", "-o", help="Path to output file", default="out.txt")

    args = parser.parse_args()
    config = parse_config(args.config)
    files = parse_files(args.path)

    if len(files) == 0:
        print("No valid PDF files found in the specified directory.")
        sys.exit(1)

    return (files, config, args.out)


def get_start_date(pdf: str) -> datetime | None:
    regex = rf"statement from ({REGEX_DATE_LONG}) to ({REGEX_DATE_LONG})"

    if match := re.search(regex, pdf, re.IGNORECASE):
        end_year = match[8]
        start_month = match[2]
        start_day = match[3]
        start_year = match[4] or end_year

        return str_to_date(f"{start_month} {start_day} {start_year}")

    return None


def get_category(description: str, lookup: Dict[str, List[str]] = None) -> str | None:
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


def parse_tx(line: str, start_date: datetime, config: dict) -> Transaction | None:
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

    if should_exclude(description, config["excludes"]):
        return None

    return tx


def parse_pdf(file_path: str, config: dict) -> List[Transaction]:
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
            if tx := parse_tx(match[0], start_date, config):
                transactions.append(tx)

    return transactions


def main():
    files, config, out_file = parse_args()
    transactions = sorted(
        [tx for file in files for tx in parse_pdf(file, config)],
        key=lambda tx: tx["date"],
    )
    out_str = "\n".join(
        format_tx(tx, format_str=OUTPUT_ROW_FORMAT, with_padding=True)
        for tx in transactions
    )

    str_to_file(out_str, out_file)

    print(out_str)
    print()
    print(
        f'Parsing files > "{out_file}"... OK: {len(transactions)} entr(ies) in result'
    )


if __name__ == "__main__":
    main()
