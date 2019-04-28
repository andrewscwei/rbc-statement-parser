# This script parses transaction rows copied directly from RBC online banking
# from within a web browser. It also works if you copied the rows from a
# downloaded VISA statement PDF (VISA only) from within Google Drive. See the
# README for more details.

import json
import re
import sys
from typing import Match

with open('config/categories.json') as json_file:
  data = json.load(json_file)
  categories = data

with open('config/excludes.json') as json_file:
  data = json.load(json_file)
  remove_lines = data['lines']
  remove_words = data['words']

tmp_prefix = '<TMP>'
tmp_code = ''.ljust(23, '0')

regex_date = r'[A-Za-z]{3} [0-9]{2}(?:, )?(?:[0-9]{4})?'
regex_amount = r'-?\$[0-9,]+\.[0-9]{2}'
regex_code = r'[0-9]{23}'

file_in = sys.argv[1]
file_out = f'{file_in}-parsed'

# Applies formatting to all lines in the statement, adding uniform spacing
# between columns.
def format_statement(match: Match) -> str:
  col_date = match.group(1).ljust(6)[:6]
  col_code = match.group(2).ljust(23)[:23]
  col_desc = match.group(3).ljust(60)[:60]
  col_amount = match.group(4).ljust(15)[:15]
  col_category = match.group(5).ljust(30)[:30]
  return r'{0}    {1}    {2}    {3}    {4}'.format(col_date, col_code, col_desc, col_category, col_amount)

print(f'Parsing file "{file_in}" > "{file_out}"...')
print()

# Store file content in string.
file = open(file_in, 'r')
read_str = file.read()
file.close()

# Count original number of lines, for output reference only.
old_cloc: int = len(read_str.split('\n'))

# Format all line chunks so each line starts with the corresponding transaction
# date. Append a new line at the end for parsing convenience later on.
read_str = re.sub(r'\n(?!{0})'.format(regex_date), ' ', read_str) + '\n'

# Remove tabs.
read_str = re.sub(r'\t', ' ', read_str)

# Remove posting date that is before the transaction date and only keep
# transaction date.
read_str = re.sub(r'({0}) ({1})'.format(regex_date, regex_date), r'\1', read_str)

# Remove the currency exchange info that is before the money amount.
read_str = re.sub(r'(Foreign Currency.*)({0})'.format(regex_amount), r'\2', read_str)

# Rearrange transaction code. The ones who don't have a trsansaction code will
# have a temporary code of all zeroes.
read_str = re.sub(r'({0}.*\n)'.format(regex_date), r'{0} \1'.format(tmp_prefix), read_str)
read_str = re.sub(r'{0} ({1})(.*)({2})(.*)'.format(tmp_prefix, regex_date, regex_code), r'\1 \3 \2 \4', read_str)
read_str = re.sub(r'{0} ({1})(.*)'.format(tmp_prefix, regex_date, regex_code), r'\1 {0} \2'.format(tmp_code), read_str)

# Remove all lines in the regexes of lines to exclude.
for regex in remove_lines:
  read_str = re.sub(re.compile('%s%s%s' % (r'(.*?)', regex, r'(.*?)\n')), '', read_str)

# Strip useless info.
for regex in remove_words:
  read_str = re.sub(re.compile(regex), '', read_str)

# Assign known categories to each transaction. If the category not known, assign
# "Others" by default. Perform this operation in 3 steps:
#   1. Add a tag to the beginning of each line. This is used to keep track of
#      whether the line has been parsed (parsed line has that tag removed).
#   2. Parse the lines and append the appropriate category at EOL.
#   3. Revisit all lines still with the tag and append "Others" to EOL.
read_str = re.sub(r'({0}.*\n)'.format(regex_date), r'{0} \1'.format(tmp_prefix), read_str)
for category in categories:
  for regex in categories[category]:
    read_str = re.sub(re.compile('%s %s%s%s' % (tmp_prefix, r'(.*?', regex, r'.*?)\n')), r'\1' + ' ' + category + r'\n', read_str)
read_str = re.sub(r'{0} (.*)\n'.format(tmp_prefix), r'\1 Others \n', read_str)

# Remove extra spaces.
read_str = re.sub(r' +', ' ', read_str)

# Apply space formatting.
read_str = re.sub(r'({0}) +({1}) +(.*) +({2}) +(.*)'.format(regex_date, regex_code, regex_amount), format_statement, read_str)

# Strip invalid transaction codes.
read_str = re.sub(r'[0]{23}', ''.ljust(23, ' '), read_str)

# Remove trailing whitespace
read_str = re.sub(r' +(\n)', r'\1', read_str)

# Write output to file.
file = open(file_out, 'w')
file.write(read_str)
file.close()

# Count total lines in output string and minus one to account for the blank line
# at EOF.
new_cloc = len(read_str.split('\n')) - 1

print(read_str)
print(f'Parsing file "{file_in}" > "{file_out}"... OK: {old_cloc} > {new_cloc} entr(ies) in result')
