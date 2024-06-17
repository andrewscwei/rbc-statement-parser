import re
from datetime import datetime
from typing import List

import fitz


def count_lines(string: str) -> int:
    """
    Counts number of lines in a string.
    """
    return len(string.split("\n"))


def file_to_str(file_path: str) -> str:
    """
    Reads a file and returns it as a string.
    """
    with open(file_path, "r", encoding="utf8") as file:
        string = file.read()

    return string


def str_to_file(string: str, file_path: str):
    """
    Writes a string to a file.
    """
    with open(file_path, "w", encoding="utf8") as file:
        file.write(string)


def trim_lines(lines: str) -> str:
    """
    Trims unwanted whitespaces.
    """
    # Remove all blank lines.
    lines = re.sub(r"(?imu)^\s*\n", r"", lines)

    # Remove consecutive spaces.
    lines = re.sub(r" +", " ", lines)

    # Remove leading white spaces.
    lines = re.sub(r"(\n) +", r"\1", lines)

    # Remove trailing white spaces.
    lines = re.sub(r" +(\n)", r"\1", lines)

    # Convert tabs to spaces.
    lines = re.sub(r"\t", " ", lines)

    return lines


def filter_lines(
    lines: str, exclude_lines: List[str] = None, exclude_words: List[str] = None
) -> str:
    """
    Filters lines in a string according to provided regex's.
    """
    if exclude_lines is not None:
        for regex in exclude_lines:
            lines = re.sub(
                re.compile("%s%s%s" % (r"(.*?)", regex, r"(.*?)\n")), "", lines
            )

    if exclude_words is not None:
        for regex in exclude_words:
            lines = re.sub(re.compile(regex), "", lines)

    return lines


def append_category(
    string: str,
    categories: dict = None,
    default_category: str = "Other",
    delimiter: str = " ",
) -> str:
    """
    Appends a category to a string by looking up the provided dictionary for
    regex matches.
    """
    if categories is None:
        categories = {}

    tmp_prefix = "<TMP>"
    string = re.sub(r"^(.*)$", rf"{tmp_prefix}\1", string)

    for category in categories:
        for regex in categories[category]:
            (string, subbed) = re.subn(
                re.compile(f"{tmp_prefix}{r'(.*?'}{regex}{r'.*?)$'}"),
                r"\1" + delimiter + category,
                string,
                1,
            )

            if subbed > 0:
                break
        if subbed > 0:
            break

    string = re.sub(
        rf"^{tmp_prefix}(.*)$", r"\1" + delimiter + default_category, string
    )

    return string


def str_to_date(string: str):
    return datetime.strptime(string, "%b %d %Y")


def ccy_to_float(ccy: str):
    return float(ccy.replace("$", "").replace(",", ""))


def pdf_to_str(file_path: str) -> str:
    document = fitz.open(file_path)
    text = ""

    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()

    return text
