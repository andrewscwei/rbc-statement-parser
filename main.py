import argparse
import json
import os
import sys

from app.chequing import is_chequing, parse_chequing
from app.entities import Config
from app.utils import format_transaction, write_file
from app.visa import is_visa, parse_visa


def parse_config(path: str) -> Config:
    # Default configuration
    default_config = {
        "format": "{date}\t{method}\t{code}\t{description}\t{category}\t{amount}",
        "categories": {},  # Empty dict instead of None
        "excludes": []     # Empty list instead of None
    }
    
    try:
        with open(path, encoding="utf8") as json_file:
            config = json.load(json_file)
            # Merge with defaults, keeping user values where they exist
            return {
                "format": config.get("format", default_config["format"]),
                "categories": config.get("categories", default_config["categories"]),
                "excludes": config.get("excludes", default_config["excludes"])
            }
    except FileNotFoundError:
        print(f"Warning: Config file '{path}' not found. Using default configuration.")
        return default_config
    except json.JSONDecodeError:
        print(f"Warning: Config file '{path}' is not valid JSON. Using default configuration.")
        return default_config
    except Exception as e:
        print(f"Warning: Error reading config file: {str(e)}. Using default configuration.")
        return default_config


def parse_files(path: str) -> list:
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


def parse_args() -> tuple[list, dict, str]:
    parser = argparse.ArgumentParser(
        description="A script that parses RBC chequing and VISA statements in PDF format and extracts transactions"
    )

    parser.add_argument("path", help="Path or to PDF or directory of PDFs")
    parser.add_argument("--config", "-c", help="Path to config file", default=".rc")
    parser.add_argument("--out", "-o", help="Path to output file")

    args = parser.parse_args()
    config = parse_config(args.config)
    files = parse_files(args.path)

    if len(files) == 0:
        print("No valid PDF files found in the specified directory.")
        sys.exit(1)

    return (files, config, args.out)


def parse_pdf(file_path: str, categories: dict, excludes: list) -> list:
    # Ensure categories and excludes are never None
    categories = categories or {}
    excludes = excludes or []
    
    if is_chequing(file_path):
        return parse_chequing(file_path, categories, excludes)

    if is_visa(file_path):
        return parse_visa(file_path, categories, excludes)

    return []


def main():
    files, config, out_file = parse_args()
    transactions = sorted(
        [
            tx
            for file in files
            for tx in parse_pdf(file, config.get("categories"), config.get("excludes"))
        ],
        key=lambda tx: tx["date"],
    )
    out_str = "\n".join(
        format_transaction(
            tx,
            template=config.get("format"),
            default_category="Other",
            padding=True,
        )
        for tx in transactions
    )

    if out_file:
        write_file(out_str, out_file)

    print(out_str)
    print()
    print(f"Parsing statements... OK: {len(transactions)} transaction(s)")


if __name__ == "__main__":
    main()