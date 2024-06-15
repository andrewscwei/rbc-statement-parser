# This script parses a copied chunk from an RBC Visa e-statement PDF. Note that
# this script does not work with other e-statement types (i.e. chequing or
# savings).

import re
import sys
from typing import Match

from parse_config import parse_config
from utils import (
    append_category,
    count_lines,
    file_to_str,
    filter_lines,
    str_to_file,
    trim_lines,
)

TMP_CODE = "".ljust(23, "0")
TMP_STR = "<TMP>"
REGEX_DATE = r"[A-Za-z]{3} [0-9]{2}(?:, )?(?:[0-9]{4})?"
REGEX_AMOUNT = r"-?\$[0-9,]+\.[0-9]{2}"
REGEX_CODE = r"[0-9]{23}"
OUTPUT_ROW_FORMAT = "{date}\t\t\t{code}\t{description}\t{category}\t{amount}"

file_in = sys.argv[1]
file_out = f"{file_in}-parsed"


def format_statement(match: Match, with_padding: bool = False) -> str:
    date = match.group(1) if not with_padding else match.group(1).ljust(6)
    code = match.group(2) if not with_padding else match.group(2).ljust(23)
    description = match.group(3) if not with_padding else match.group(3).ljust(60)
    amount = match.group(4) if not with_padding else match.group(4).ljust(15)
    category = match.group(5) if not with_padding else match.group(5).ljust(30)

    # Strip invalid transaction codes.
    if code == TMP_CODE:
        code = "" if not with_padding else "".ljust(23)

    return OUTPUT_ROW_FORMAT.format(
        date=date,
        code=code,
        description=description,
        amount=f"-{amount}",
        category=category,
    )


def format_statement_with_padding(match: Match) -> str:
    return format_statement(match, True)


def main():
    config = parse_config()

    # Prepare for parsing.
    print(f'Parsing file "{file_in}" > "{file_out}"...')
    print()

    read_str = file_to_str(file_in)
    write_str = ""
    old_count = count_lines(read_str)

    # Begin parsing.

    # Group strings into line-delimited transactions.
    read_str = re.sub(rf"\n(?!{REGEX_DATE})", " ", read_str) + "\n"

    # Remove all lines that are not part of the transaction details.
    read_str = filter_lines(read_str, config["exclude_lines"], config["exclude_words"])

    # Remove all unnecessary whitespaces.
    read_str = trim_lines(read_str)

    # Remove posting date that is before the transaction date and only keep
    # transaction date.
    read_str = re.sub(rf"({REGEX_DATE}) ({REGEX_DATE})", r"\1", read_str)

    # Remove the currency exchange info that is before the money amount.
    # read_str = re.sub(
    #     r"(Foreign Currency.*)({0})".format(REGEX_AMOUNT), r"\2", read_str
    # )

    # Rearrange transaction code. The ones who don't have a transaction code
    # will have a temporary code of all zeroes.
    read_str = re.sub(rf"({REGEX_DATE}.*\n)", rf"{TMP_STR}\1", read_str)
    read_str = re.sub(
        rf"{TMP_STR}({REGEX_DATE})(.*)({REGEX_CODE})(.*)", r"\1 \3 \2 \4", read_str
    )
    read_str = re.sub(rf"{TMP_STR}({REGEX_DATE})(.*)", rf"\1 {TMP_CODE} \2", read_str)

    for line in read_str.splitlines():
        match = re.findall(rf"{REGEX_AMOUNT}", line)

        # If there are more than one money amount detected, only use the first
        # one.
        if match:
            line = re.sub(rf"{REGEX_AMOUNT}.*$", "", line)
            line += f"{ match[0]}"

        line = append_category(line, config["categories"], "Other")
        formatted_str = re.sub(
            rf"({REGEX_DATE}) +({REGEX_CODE}) +(.*) +({REGEX_AMOUNT}) +(.*)",
            format_statement,
            line,
        )
        write_str += formatted_str
        write_str += "\n"

        print(
            re.sub(
                rf"({REGEX_DATE}) +({REGEX_CODE}) +(.*) +({REGEX_AMOUNT}) +(.*)",
                format_statement_with_padding,
                line,
            )
        )

    # End parsing.
    str_to_file(write_str, file_out)
    new_count = count_lines(write_str) - 1

    print()
    print(
        f'Parsing file "{file_in}" > "{file_out}"... OK: {old_count} > {new_count} entr(ies) in result'
    )


if __name__ == "__main__":
    main()
