# This script parses a copied chunk from an e-statement PDF of an RBC chequing/savings account. Note
# that this script does not work with VISA e-statement PDFs because the format is different.
#
# Consider that a single transaction (once copied over) can span over multiple lines. Here are some
# known patterns:
#   1. A complete transaction MAY or MAY NOT begin with a date. If it doesn't begin with a date, its
#      date is the date of the previous transaction.
#   2. A complete transaction ALWAYS has AT LEAST one money amount. So it can have more than one,
#      i.e. a deposit amount followed by the current balance.
#   3. A complete transaction ALWAYS ends with a money amount.
#
# Given the above info, use the following strategy when parsing:
#   1. Parse the file line by line.
#   2. Observe the beginning of line:
#        a. If it starts with a date, create a new text stream and copy the date + rest of the line
#           into the stream.
#        b. If it doesn't start with a date:
#             i. Check if the text stream is empty. If it is, this is a new transaction with the
#                same date as the last transaction. Do step 2a with the last known date.
#             ii. If the text stream is not empty, this is a continuation of the previous line,
#                 still on the same transaction. Copy the rest of the line to the current text
#                 stream, which should already contain the previous line.
#   3. Observe the end of line:
#        a. If it ends with a money amount, the transaction completes. Re-append this line to the
#           current text stream up to the first found money amount. Discard the rest of the money
#           amounts in the same line anyway because the second money amount (shouldn't have more
#           than 2) always represents the balance, which is irrelevant. Append the text stream to
#           the output as a new line, then clear the text stream.
#        b. If it doesn't end with a money amount, we are expecting the next line to be a
#           continuation of the current transaction.
#   4. Repeat from step 1 until all lines are parsed.
#   5. Now that we have a string with each line corresponding to a transaction, apply bulk parsing.

import re
import sys
from typing import Match

from utils import (
    append_category_eol,
    cloc,
    file_to_str,
    optimize_whitespaces,
    redact_lines,
    str_to_file,
)

REGEX_DATE = r"[0-9]{1,2} [A-Z][a-z]{2}"
REGEX_AMOUNT = r"-?[0-9,]+\.[0-9]{2}"
OUTPUT_ROW_FORMAT = "{date}\t\t\t\t{description}\t{category}\t{amount}"

file_in = sys.argv[1]
file_out = f"{file_in}-parsed"


def format_statement(match: Match, with_padding: bool = False) -> str:
    date = match.group(1) if not with_padding else match.group(1).ljust(6)
    description = match.group(2) if not with_padding else match.group(2).ljust(60)
    amount = match.group(3) if not with_padding else match.group(3).ljust(15)
    category = match.group(4) if not with_padding else match.group(4).ljust(30)

    return OUTPUT_ROW_FORMAT.format(
        date=date, description=description, amount=amount, category=category
    )


def format_statement_with_padding(match: Match) -> str:
    return format_statement(match, True)


# Prepare for parsing.
print(f'Parsing file "{file_in}" > "{file_out}"...')
print()

read_str = file_to_str(file_in)
write_str = ""
old_cloc = cloc(read_str)
curr_stream = ""
curr_date = None

# Begin parsing.
read_str = optimize_whitespaces(read_str)

# Begin parsing the file so that each line ends up corresponding to a transaction.
for line in read_str.splitlines():
    line = line.strip()

    # Check if line starts with a date.
    m1 = re.search(rf"^{REGEX_DATE}", line)

    # If line starts with a date, cache the date and open a new stream and append the date to it.
    if m1:
        curr_date = m1.group()
        curr_stream = f"{curr_date} "
        line = re.sub(rf"^{REGEX_DATE} +(.*)", r"\1", line)
    # Otherwise check if this line is a continuation of the previous line. If not then
    elif curr_stream == "":
        curr_stream = f"{curr_date} "

    # Check if remainder of the line ends with a money amount.
    m2 = re.findall(rf"{REGEX_AMOUNT}", line)

    # If it does, the transaction ends here. Append the line (up to the first money amount) to output
    # and clear it for the next transaction.
    if m2:
        line = re.sub(rf"{REGEX_AMOUNT}.*$", "", line)
        curr_stream += f"{line} ${m2[0]}"
        curr_stream = append_category_eol(curr_stream)
        formatted_str = re.sub(
            rf"({REGEX_DATE}) +(.*) +(\${REGEX_AMOUNT}) +(.*)",
            format_statement,
            curr_stream,
        )
        write_str += formatted_str
        write_str += "\n"

        print(
            re.sub(
                rf"({REGEX_DATE}) +(.*) +(\${REGEX_AMOUNT}) +(.*)",
                format_statement_with_padding,
                curr_stream,
            )
        )

        curr_stream = ""
    else:
        curr_stream += f" {line}"

write_str = redact_lines(write_str)

# End parsing.
str_to_file(write_str, file_out)

new_cloc = cloc(write_str) - 1

print()
print(
    f'Parsing file "{file_in}" > "{file_out}"... OK: {old_cloc} > {new_cloc} entr(ies) in result'
)
