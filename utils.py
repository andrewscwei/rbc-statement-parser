import json
import re

with open('config/categories.json') as json_file:
  data = json.load(json_file)
  categories = data

with open('config/excludes.json') as json_file:
  data = json.load(json_file)
  remove_lines = data['lines']
  remove_words = data['words']

def cloc(s: str) -> int:
  '''
  Counts the number of lines in a string.

  Arguments:
    s {str} - The string to count.

  Returns:
    {int} The number of lines.
  '''
  return len(s.split('\n'))

def file_to_str(file_path: str) -> str:
  '''
  Reads a file and returns it as a string.

  Arguments:
    file_path {str} - The path to the file.

  Returns:
    {str} The string representation of the file.
  '''
  file = open(file_path, 'r')
  read_str = file.read()
  file.close()

  return read_str

def str_to_file(write_str: str, file_path: str):
  '''
  Writes a string to a file.

  Arguments:
    write_str {str} - The string to write to the file.
    file_path {str} - The path to the file to write to.
  '''
  file = open(file_path, 'w')
  file.write(write_str)
  file.close()

def optimize_whitespaces(s: str) -> str:
  '''
  Removes extraneous whitespaces from each line of a string.

  Arguments:
    s {str} - The string to optimize.

  Returns:
    {str} The optimized string.
  '''
  # Remove all blank lines.
  s = re.sub(r'(?imu)^\s*\n', r'', s)

  # Remove consecutive spaces.
  s = re.sub(r' +', ' ', s)

  # Remove leading white spaces.
  s = re.sub(r'(\n) +', r'\1', s)

  # Remove trailing white spaces.
  s = re.sub(r' +(\n)', r'\1', s)

  return s

def redact_lines(s: str) -> str:
  '''
  Applies redactions all lines in a string according to the dictionary of lines
  to exclude and words to exclude.

  Arguments:
    s {str} - The string to apply the redactions to.

  Returns:
    {str} - The redacted string.
  '''
  # Remove unwanted lines.
  for regex in remove_lines:
    s = re.sub(re.compile('%s%s%s' % (r'(.*?)', regex, r'(.*?)\n')), '', s)

  # Remove unwanted words.
  for regex in remove_words:
    s = re.sub(re.compile(regex), '', s)

  return s

def append_category_eol(line: str, delimiter: str = ' ') -> str:
  '''
  Assigns a category to a line by refering to the JSON dictionary of categoryes.
  If the category not known, assign "Others" by default. Perform this operation
  in 3 steps:
    1. Add a tag to the beginning of the line. This is used to keep track of
       whether the line has been parsed (parsed line has that tag removed).
    2. Parse the line and append the appropriate category at EOL, separated by
       the specified delimiter.
    3. Check if line has category by seeing if it has the tag in front of it. If
       so, append "Others" to EOL, separated by the specified delimiter.

  Arguments:
    line {str} - The line to parse.
    delimiter {str} - The delimter to separate the original line and the assigned category. (default: {' '})

  Returns:`
    {str} The original line with a category appended to it.
  '''
  default_category = 'Others'
  tmp_prefix = '<TMP>'
  line = re.sub(r'^(.*)$', r'{}\1'.format(tmp_prefix), line)

  for category in categories:
    for regex in categories[category]:
      line = re.sub(
        re.compile('%s%s%s%s' % (
          tmp_prefix,
          r'(.*?',
          regex,
          r'.*?)$',
        )),
        r'\1' + delimiter + category,
        line
      )

  line = re.sub(r'^{}(.*)$'.format(tmp_prefix), r'\1' + delimiter + 'Others', line)

  return line

