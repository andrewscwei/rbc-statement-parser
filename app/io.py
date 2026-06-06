import os

import fitz


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
