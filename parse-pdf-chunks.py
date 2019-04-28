# This script parses a copied chunk from an e-statement PDF of an RBC
# chequing/saving account. Note that this script does not work with VISA
# e-statement PDFs because the format is different. In order for this script to
# work, you MUST open the PDF in Google Drive and copy the statement tables with
# the selection caret starting at the first character of the date of the first
# transaction, and ending at the last character of the money amount of the last
# statement. Page breaks are not accounted for, so copy the statements in the
# table PER PAGE. Copy all of these entries into a text file, then run this
# script against it.
#
# Consider that a single transaction (once copied over) can span over multiple
# lines. Here are some known patterns:
#   1. A complete transaction MAY or MAY NOT begin with a date. If it doesn't
#      begin with a date, its date is the date of the previous transaction.
#   2. A complete transaction ALWAYS has AT LEAST one money amount. So it can
#      have more than one, i.e. a deposit amount followed by the current
#      balance.
#   3. A complete transaction ALWAYS ends with a money amount.
#
# Given the above info, use the following strategy when parsing:
#   1. Parse the file line by line.
#   2. Observe the beginning of line:
#        a. If it starts with a date, create a new text stream and copy the
#           date + rest of the line into the stream.
#        b. If it doesn't start with a date:
#             i. Check if the text stream is empty. If it is, this is a new
#                transaction with the same date as the last transaction. Do
#                step 2a with the last known date.
#            ii. If the text stream is not empty, this is a continuation of the
#                previous line, still on the same transaction. Copy the rest of
#                the line to the current text stream, which should already
#                contain the previous line.
#   3. Observe the end of line:
#        a. If it ends with a money amount, the transaction completes. Reappend
#           this line to the curren text stream up to the first found money
#           amount. Discard the rest of the money amounts in the same line
#           anyway because the second money amount (shouldn't have more than 2)
#           always represents the balance, which is irrelevant. Append the
#           text stream to the output as a new line, then clear the text stream.
#        b. If it doesn't end with a money amount, we are expecting the next
#           line to be a continuation of the current transaction.
#   4. Repeat from step 1 until all lines are parsed.
#   5. Now that we have a string with each line corresponding to a transaction,
#      apply bulk parsing.

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

regex_date = r'[0-9]{1,2} [A-Z][a-z]{2}'
regex_amount = r'-?[0-9,]+\.[0-9]{2}'
regex_code = r'[0-9]{23}'

file_in = sys.argv[1]
file_out = f'{file_in}-parsed'

# Applies formatting to all lines in the statement, adding uniform spacing
# between columns.
def format_statement(match: Match) -> str:
  col_date = match.group(1).ljust(6)
  col_desc = match.group(2).ljust(50)
  col_amount = match.group(3).ljust(15)
  col_category = match.group(4).ljust(30)
  return r'{0}	{1}	{2}	{3}'.format(col_date, col_desc, col_category, col_amount)

print(f'Parsing file "{file_in}" > "{file_out}"...')
print()

# Store file content in string.
file = open(file_in, 'r')
read_str = file.read()
file.close()

# Count original number of lines, for output reference only.
old_cloc: int = len(read_str.split('\n'))

output = ''
curr_stream = ''
curr_date = None

# Remove tabs.
read_str = re.sub(r'\t', ' ', read_str)

# Begin parsing the file so that each line ends up corresponding to a
# transaction.
for line in read_str.splitlines():
  line = line.strip()

  # Check if line starts with a date.
  m1 = re.search(r'^{0}'.format(regex_date), line)

  # If line starts with a date, cache the date and open a new stream and append
  # the date to it.
  if m1:
    curr_date = m1.group()
    curr_stream = f'{curr_date} '
    line = re.sub(r'^{0} +(.*)'.format(regex_date), r'\1', line)
  # Otherwise check if this line is a continuation of the previous line. If not
  # then
  elif curr_stream is '':
    curr_stream = f'{curr_date} '

  # Check if remainder of the line ends with a money amount.
  m2 = re.findall(r'{0}'.format(regex_amount), line)

  # If it does, the transaction ends here. Append the line (up to the first
  # money amount) to output and clear it for the next transaction.
  if m2:
    line = re.sub(r'{0}.*$'.format(regex_amount), '', line)
    curr_stream += f'{line} ${m2[0]}'
    output += curr_stream
    output += '\n'
    curr_stream = ''
  else:
    curr_stream += f' {line}'

# Remove all lines in the regexes of lines to exclude.
for regex in remove_lines:
  output = re.sub(re.compile('%s%s%s' % (r'(.*?)', regex, r'(.*?)\n')), '', output)

# Strip useless info.
for regex in remove_words:
  output = re.sub(re.compile(regex), '', output)

# Assign known categories to each transaction. If the category not known, assign
# "Others" by default. Perform this operation in 3 steps:
#   1. Add a tag to the beginning of each line. This is used to keep track of
#      whether the line has been parsed (parsed line has that tag removed).
#   2. Parse the lines and append the appropriate category at EOL.
#   3. Revisit all lines still with the tag and append "Others" to EOL.
output = re.sub(r'({0}.*\n)'.format(regex_date), r'{0} \1'.format(tmp_prefix), output)
for category in categories:
  for regex in categories[category]:
    output = re.sub(re.compile('%s %s%s%s' % (tmp_prefix, r'(.*?', regex, r'.*?)\n')), r'\1' + ' ' + category + r'\n', output)
output = re.sub(r'{0} (.*)\n'.format(tmp_prefix), r'\1 Others \n', output)

# Remove extra spaces.
output = re.sub(r' +', ' ', output)

# Apply space formatting.
output = re.sub(r'({0}) +(.*) +(\${1}) +(.*)'.format(regex_date, regex_amount), format_statement, output)

# Remove trailing whitespace
output = re.sub(r' +(\n)', r'\1', output)

# Write output to file.
file = open(file_out, 'w')
file.write(output)
file.close()

# Count total lines in output string and minus one to account for the blank line
# at EOF.
new_cloc = len(output.split('\n')) - 1

print(output)
print(f'Parsing file "{file_in}" > "{file_out}"... OK: {old_cloc} > {new_cloc} entr(ies) in result')
