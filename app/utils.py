from datetime import datetime

import fitz


def str_to_date(string: str):
    return datetime.strptime(string, "%b %d %Y")


def ccy_to_float(ccy: str):
    return float(ccy.replace("$", "").replace(",", ""))


def file_to_str(file_path: str) -> str:
    """
    Reads a file and returns it as a string.
    """
    if file_path.lower().endswith(".pdf"):
        document = fitz.open(file_path)
        string = ""

        for page_num in range(len(document)):
            page = document.load_page(page_num)
            string += page.get_text()

        return string

    with open(file_path, "r", encoding="utf8") as file:
        string = file.read()

    return string


def str_to_file(string: str, file_path: str):
    """
    Writes a string to a file.
    """
    with open(file_path, "w", encoding="utf8") as file:
        file.write(string)
