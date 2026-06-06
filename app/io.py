import os

import fitz


def read_pdf(file_path: str, html: bool = False) -> str:
    """Read the contents of a PDF file and return it as a string. If `html` is
    True, returns the text in HTML format; otherwise, returns plain text.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")

    if not file_path.lower().endswith(".pdf"):
        raise TypeError(f"File {file_path} is not a recognized PDF")

    document = fitz.open(file_path)
    string = ""

    for page_num in range(len(document)):
        page = document.load_page(page_num)
        string += page.get_text("html" if html else "text")

    return string


def read_file(file_path: str) -> str:
    """Read the contents of a text file and return it as a string."""

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")

    with open(file_path, "r", encoding="utf8") as file:
        string = file.read()

    return string


def write_file(string: str, file_path: str):
    """Write a string to a text file at the specified path."""

    with open(file_path, "w", encoding="utf8") as file:
        file.write(string)
