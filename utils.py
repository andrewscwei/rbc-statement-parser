import json
import re

with open('config/categories.json', encoding='utf8') as json_file:
  data = json.load(json_file)
  categories = data

with open('config/excludes.json', encoding='utf8') as json_file:
  data = json.load(json_file)
  remove_lines = data['lines']
  remove_words = data['words']

def cloc(str: str) -> int:
  '''
  Counts the number of lines in a string.

  Arguments:
    str {str} - The string to count.

  Returns:
    {int} The number of lines.
  '''
  return len(str.split('\n'))

def file_to_str(file_path: str) -> str:
  '''
  Reads a file and returns it as a string.

  Arguments:
    file_path {str} - The path to the file.

  Returns:
    {str} The string representation of the file.
  '''
  with open(file_path, 'r', encoding='utf8') as file:
    read_str = file.read()

  return read_str

def str_to_file(write_str: str, file_path: str):
  '''
  Writes a string to a file.

  Arguments:
    write_str {str} - The string to write to the file.
    file_path {str} - The path to the file to write to.
  '''
  with open(file_path, 'w', encoding='utf8') as file:
    file.write(write_str)

def optimize_whitespaces(str: str) -> str:
  '''
  Removes extraneous whitespaces from each line of a string.

  Arguments:
    str {str} - The string to optimize.

  Returns:
    {str} The optimized string.
  '''
  # Remove all blank lines.
  str = re.sub(r'(?imu)^\s*\n', r'', str)

  # Remove consecutive spaces.
  str = re.sub(r' +', ' ', str)

  # Remove leading white spaces.
  str = re.sub(r'(\n) +', r'\1', str)

  # Remove trailing white spaces.
  str = re.sub(r' +(\n)', r'\1', str)

  # Convert tabs to spaces.
  str = re.sub(r'\t', ' ', str)

  return str

def redact_lines(str: str) -> str:
  '''
  Redacts all lines in a string according to the dictionary of lines to exclude and words to
  exclude.

  Arguments:
    str {str} - The string to redact.

  Returns:
    {str} - The redacted string.
  '''
  # Remove unwanted lines.
  for regex in remove_lines:
    str = re.sub(re.compile('%s%s%s' % (r'(.*?)', regex, r'(.*?)\n')), '', str)

  # Remove unwanted words.
  for regex in remove_words:
    str = re.sub(re.compile(regex), '', str)

  return str

def append_category_eol(line: str, delimiter: str = ' ') -> str:
  '''
  Assigns a category to a line by referring to the JSON dictionary of categories. If the category not
  known, assign "Other" by default. Perform this operation in 3 steps:
    1. Add a tag to the beginning of the line. This is used to keep track of whether the line has
       been parsed (parsed line has that tag removed).
    2. Parse the line and append the appropriate category at EOL, separated by the specified
       delimiter.
    3. Check if line has category by seeing if it has the tag in front of it. If so, append "Other"
       to EOL, separated by the specified delimiter.

  Arguments:
    line {str} - The line to parse. delimiter {str} - The delimiter to separate the original line and
    the assigned category. (default: {' '})

  Returns:`
    {str} The original line with a category appended to it.
  '''
  default_category = 'Other'
  tmp_prefix = '<TMP>'
  line = re.sub(r'^(.*)$', fr'{tmp_prefix}\1', line)

  for category in categories:
    for regex in categories[category]:
      (line, subbed) = re.subn(
        re.compile(f"{tmp_prefix}{r'(.*?'}{regex}{r'.*?)$'}"),
        r'\1' + delimiter + category,
        line,
        1,
      )

      if subbed > 0:
        break
    if subbed > 0:
      break

  line = re.sub(fr'^{tmp_prefix}(.*)$', r'\1' + delimiter + default_category, line)

  return line
