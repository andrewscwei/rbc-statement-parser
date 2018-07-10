import re
import sys

# Formats a line in the statement, with each field separated with spaces.
def format_statement(m):
  return r'{0} {1} {2}'.format('{:<18}'.format(m.group(1)), '{:<60}'.format(re.sub('[^A-Za-z0-9 ]+', '', m.group(2))), m.group(3))

# Get input file from args.
filein = sys.argv[1]

# Regex for dates.
dateregex = r'[A-Za-z]{3} [0-9]{2}(?:, )?(?:[0-9]{4})?'

# Regex for transaction codes.
coderegex = '[0-9]{23}'

# Regex for money values.
valueregex = r'-?\$[0-9,]+.?[0-9]{2}'

# Store file content in string.
file = open(filein, 'r')
readstr = file.read()
file.close()

# Remove blank lines
readstr = re.sub(r'\n(?!({0}))'.format(dateregex), ' ', readstr)

# Remove posting date, only keep transaction date.
readstr = re.sub(r'({0}) ({1})'.format(dateregex, dateregex), r'\1', readstr)

# Remove currency exchange info.
readstr = re.sub(r'(Foreign Currency.*)(\$)', r'\2', readstr)

# Remove transaction code.
readstr = re.sub(r'{0}'.format(coderegex), '', readstr)

# Remove tabs.
readstr = re.sub(r'\t', ' ', readstr)

# Remove extra spaces.
readstr = re.sub(r' +', ' ', readstr)

# Remove payments.
readstr = re.sub(r'(.*?)PAYMENT - THANK YOU(.*?)\n', '', readstr)

# Isolate money value.
readstr = re.sub(r'({0}) +(.*) +({1}) +({2})'.format(dateregex, valueregex, valueregex), format_statement, readstr)
readstr = re.sub(r'({0}) +(.*) +({1})'.format(dateregex, valueregex), format_statement, readstr)

# Remove trailing whitespace
readstr = re.sub(r' +(\n)', r'\1', readstr)

# Overwrite original file.
file = open(filein, 'w')
file.write(readstr)
file.close()