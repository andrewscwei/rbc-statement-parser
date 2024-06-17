import argparse
import json
import os
import sys
from typing import List

from app.chequing import parse_chequing
from app.utils import format_transaction, write_file
from app.visa import parse_visa

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
    parser.add_argument("--out", "-o", help="Path to output file")

    args = parser.parse_args()
    config = parse_config(args.config)
    files = parse_files(args.path)

    if len(files) == 0:
        print("No valid PDF files found in the specified directory.")
        sys.exit(1)

    return (files, config, args.out)


def main():
    files, config, out_file = parse_args()
    transactions = sorted(
        [
            tx
            for file in files
            for tx in parse_visa(file, config["categories"], config["excludes"])
            # for tx in parse_chequing(file, config["categories"], config["excludes"])
        ],
        key=lambda tx: tx["date"],
    )
    out_str = "\n".join(
        format_transaction(tx, template=OUTPUT_ROW_FORMAT, padding=True)
        for tx in transactions
    )

    if out_file:
        write_file(out_str, out_file)

    print(out_str)
    print()
    print(f"Parsing statements... OK: {len(transactions)} transaction(s)")


if __name__ == "__main__":
    main()
