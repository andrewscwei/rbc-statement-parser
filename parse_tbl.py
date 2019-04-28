# This script parses transaction rows copied directly from RBC online banking
# from within a web browser. It also works if you copied the rows from a
# downloaded VISA statement PDF (VISA only) from within Google Drive. See the
# README for more details.

import re
import sys
from typing import Match

from utils import (append_category_eol, cloc, file_to_str,
                   optimize_whitespaces, redact_lines, str_to_file)

tmp_code = ''.ljust(23, '0')

regex_date = r'[A-Za-z]{3} [0-9]{2}(?:, )?(?:[0-9]{4})?'
regex_amount = r'-?\$[0-9,]+\.[0-9]{2}'
regex_code = r'[0-9]{23}'

file_in = sys.argv[1]
file_out = f'{file_in}-parsed'

output_row_format = '{date}\t\t\t{code}\t{description}\t{category}\t{amount}'

# Applies formatting to all lines in the statement, adding uniform spacing
# between columns.
def format_statement(match: Match) -> str:
  date = match.group(1)
  code = match.group(2)
  description = match.group(3)
  amount = match.group(4)
  category = match.group(5)

  # Strip invalid transaction codes.
  if code == tmp_code:
    code = ''

  return output_row_format.format(date=date, code=code, description=description, amount=amount, category=category)

# Prepare for parsing.
print(f'Parsing file "{file_in}" > "{file_out}"...')
print()

read_str = file_to_str(file_in)
write_str = ''
old_cloc = cloc(read_str)

# Begin parsing.

# Format all line chunks so each line starts with the corresponding transaction
# date. Append a new line at the end for parsing convenience later on.
read_str = re.sub(r'\n(?!{0})'.format(regex_date), ' ', read_str) + '\n'

read_str = redact_lines(read_str)
read_str = optimize_whitespaces(read_str)

# Remove posting date that is before the transaction date and only keep
# transaction date.
read_str = re.sub(r'({0}) ({1})'.format(regex_date, regex_date), r'\1', read_str)

# Remove the currency exchange info that is before the money amount.
read_str = re.sub(r'(Foreign Currency.*)({0})'.format(regex_amount), r'\2', read_str)

# Rearrange transaction code. The ones who don't have a trsansaction code will
# have a temporary code of all zeroes.
read_str = re.sub(r'({0}.*\n)'.format(regex_date), r'{0}\1'.format('<TMP>'), read_str)
read_str = re.sub(r'{0}({1})(.*)({2})(.*)'.format('<TMP>', regex_date, regex_code), r'\1 \3 \2 \4', read_str)
read_str = re.sub(r'{0}({1})(.*)'.format('<TMP>', regex_date, regex_code), r'\1 {0} \2'.format(tmp_code), read_str)

for line in read_str.splitlines():
  line = append_category_eol(line)
  formatted_str = re.sub(r'({0}) +({1}) +(.*) +({2}) +(.*)'.format(regex_date, regex_code, regex_amount), format_statement, line)
  write_str += formatted_str
  write_str += '\n'

  print(formatted_str)

# End parsing.
str_to_file(write_str, file_out)
new_cloc = cloc(write_str) - 1

print()
print(f'Parsing file "{file_in}" > "{file_out}"... OK: {old_cloc} > {new_cloc} entr(ies) in result')
