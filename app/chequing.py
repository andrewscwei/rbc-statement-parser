import re
from datetime import datetime
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from .entities import Transaction
from .utils import match_category, parse_float, read_pdf, should_exclude

PAT_FILE_PATH = r"chequing statement"
PAT_MONTH_SHORT = r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
PAT_MONTH_LONG = r"january|february|march|april|may|june|july|august|september|october|november|december"
PAT_DAY = r"\d{1,2}"
PAT_YEAR = r"\d{4}"
PAT_DATE_SHORT = rf"{PAT_DAY} (?:{PAT_MONTH_SHORT})"
PAT_DATE_LONG = rf"((?:{PAT_MONTH_LONG})) ({PAT_DAY})(?:, )?({PAT_YEAR})?"
PAT_AMOUNT = r"-?\$?[\d,]+\.\d{2}"


def is_chequing(file_path: str) -> bool:
    return bool(re.search(PAT_FILE_PATH, file_path, re.IGNORECASE))


def extract_start_date(pdf: str) -> datetime | None:
    regex = rf"from ({PAT_DATE_LONG}) to ({PAT_DATE_LONG})"

    if match := re.search(regex, pdf, re.IGNORECASE):
        end_year = match[8]
        start_month = match[2]
        start_day = match[3]
        start_year = match[4] or end_year

        return datetime.strptime(f"{start_month} {start_day} {start_year}", "%B %d %Y")

    return None


def parse_date(string: str) -> datetime:
    return datetime.strptime(string, "%d %b %Y")


def validate_transaction(tx: Transaction) -> bool:
    if not tx.get("date"):
        return False
    if not tx.get("amount"):
        return False
    if not tx.get("description"):
        return False

    return True


def extract_left_padding(soup: BeautifulSoup) -> float:
    style = soup.p.attrs["style"]
    match = re.search(r"left:([0-9.]+)pt", style, re.IGNORECASE)
    padding = float(match.group(1)) if match else 0

    return padding


def extract_date(soup: BeautifulSoup, start_date: datetime) -> Optional[str]:
    padding = extract_left_padding(soup)

    if (10 < padding < 20 or 40 < padding < 50) and re.match(
        rf"^{PAT_DATE_SHORT}$", soup.text, re.IGNORECASE
    ):
        ref_date = parse_date(f"{soup.text} {start_date.year}")
        ref_year = start_date.year + (1 if ref_date.month < start_date.month else 0)

        return parse_date(f"{soup.text} {ref_year}")

    return None


def extract_description(soup: BeautifulSoup) -> Optional[str]:
    padding = extract_left_padding(soup)

    if 60 < padding < 75 or 85 < padding < 100:
        return soup.text

    return None


def extract_withdrawal_amount(soup: BeautifulSoup) -> Optional[float]:
    padding = extract_left_padding(soup)

    if 250 < padding < 360 and re.match(rf"^{PAT_AMOUNT}$", soup.text, re.IGNORECASE):
        return parse_float(soup.text)

    return None


def extract_deposit_amount(soup: BeautifulSoup) -> Optional[float]:
    padding = extract_left_padding(soup)

    if 360 < padding < 460 and re.match(rf"^{PAT_AMOUNT}$", soup.text, re.IGNORECASE):
        return parse_float(soup.text)

    return None


def extract_balance_amount(soup: BeautifulSoup) -> Optional[float]:
    padding = extract_left_padding(soup)

    if 460 < padding < 600 and re.match(rf"^{PAT_AMOUNT}$", soup.text, re.IGNORECASE):
        return parse_float(soup.text)

    return None


def parse_chequing(
    pdf_path: str,
    categories: Dict[str, List[str]] = None,
    excludes: List[str] = None,
) -> List[Transaction]:
    pdf = read_pdf(pdf_path, html=True)
    start_date = extract_start_date(pdf)
    lines = pdf.splitlines()
    transactions = []
    pat = r"^<p.*</p>$"

    tx = {}

    for line in lines:
        if re.match(pat, line, re.IGNORECASE):
            soup = BeautifulSoup(line, "html.parser")

            if date := extract_date(soup, start_date=start_date):
                tx["date"] = date
            elif tx.get("date") and extract_description(soup):
                if tx.get("description"):
                    tx["description"] += f" {soup.text}"
                else:
                    tx["description"] = soup.text
            elif tx.get("description") and extract_withdrawal_amount(soup):
                tx["amount"] = parse_float(soup.text) * -1
            elif tx.get("description") and extract_deposit_amount(soup):
                tx["amount"] = parse_float(soup.text)

            if validate_transaction(tx):
                tx["method"] = "chequing"
                tx["category"] = match_category(tx.get("description"), categories)
                tx["posting_date"] = tx.get("date")

                if not should_exclude(tx.get("description"), excludes):
                    transactions.append(tx)

                tx = {
                    "date": tx.get("date"),
                }

    return transactions
