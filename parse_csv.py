# This script parses a CSV file downloaded directly from RBC online banking. See the README for more
# details.

import re
import sys
from typing import List

from utils import (append_category_eol, cloc, file_to_str,
                   optimize_whitespaces, redact_lines, str_to_file)

INPUT_COLS = ['account_type', 'account_number', 'date', 'cheque_number', 'description_1', 'description_2', 'cad', 'usd', 'category']
INPUT_DELIMITER = ','
OUTPUT_ROW_FORMAT = '{date}\t{account}\t\t{code}\t{description}\t{category}\t{amount}'

file_in = sys.argv[1]
file_out = f'{file_in}-parsed'

def format_statement(cols: List[str], with_padding: bool = False) -> str:
  account = cols[INPUT_COLS.index('account_type')] + ' ***' + cols[INPUT_COLS.index('account_number')][-4:]
  date = cols[INPUT_COLS.index('date')]
  code = cols[INPUT_COLS.index('cheque_number')]
  description = re.sub(r'"(.*)"', r'\1', cols[INPUT_COLS.index('description_1')]) + ' ' + re.sub(r'"(.*)"', r'\1', cols[INPUT_COLS.index('description_2')])
  amount = re.sub(r'^-?(.*)$', r'$\1', cols[INPUT_COLS.index('cad')])
  category = cols[INPUT_COLS.index('category')]

  return OUTPUT_ROW_FORMAT.format(date=date, account=account, code=code, description=description, amount=amount, category=category)

# Prepare for parsing.
print(f'Parsing file "{file_in}" > "{file_out}"...')
print()

read_str = file_to_str(file_in)
write_str = ''
old_cloc = cloc(read_str)

# Begin parsing.
read_str = optimize_whitespaces(read_str)
read_str = redact_lines(read_str)

for line in read_str.splitlines():
  line = append_category_eol(line, '')
  cols = line.split(INPUT_DELIMITER)
  formatted_str = format_statement(cols)
  write_str += formatted_str
  write_str += '\n'

  print(formatted_str)

# End parsing.
new_cloc = cloc(write_str)

str_to_file(write_str, file_out)

print()
print(f'Parsing file "{file_in}" > "{file_out}"... OK: {old_cloc} > {new_cloc} entr(ies) in result')
