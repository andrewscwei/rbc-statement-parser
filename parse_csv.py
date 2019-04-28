# This script parses a CSV file downloaded directly from RBC online banking.
# See the README for more details.

import re
import sys
from typing import List

from utils import (append_category_eol, cloc, file_to_str,
                   optimize_whitespaces, redact_lines, str_to_file)

input_cols = ['account_type', 'account_number', 'date', 'cheque_number', 'description_1', 'description_2', 'cad', 'usd', 'category']
input_delimiter = ','
output_row_format = '{date}\t{account}\t\t{code}\t{description}\t{category}\t{amount}'

file_in = sys.argv[1]
file_out = f'{file_in}-parsed'

def format_statement(cols: List[str]) -> str:
  account = cols[input_cols.index('account_type')] + ' ***' + cols[input_cols.index('account_number')][-4:]
  date = cols[input_cols.index('date')]
  code = cols[input_cols.index('cheque_number')]
  description = re.sub(r'"(.*)"', r'\1', cols[input_cols.index('description_1')]) + ' ' + re.sub(r'"(.*)"', r'\1', cols[input_cols.index('description_2')])
  amount = re.sub(r'^-?(.*)$', r'$\1', cols[input_cols.index('cad')])
  category = cols[input_cols.index('category')]

  return output_row_format.format(date=date, account=account, code=code, description=description, amount=amount, category=category)

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
  cols = line.split(input_delimiter)
  formatted_str = format_statement(cols)
  write_str += formatted_str
  write_str += '\n'

  print(formatted_str)

# End parsing.
new_cloc = cloc(write_str)

str_to_file(write_str, file_out)

print()
print(f'Parsing file "{file_in}" > "{file_out}"... OK: {old_cloc} > {new_cloc} entr(ies) in result')
