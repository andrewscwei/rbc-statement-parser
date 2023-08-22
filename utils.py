import json
import re

CATEGORIES = {}
REMOVE_LINES = []
REMOVE_WORDS = []

try:
    with open(".config", encoding="utf8") as json_file:
        data = json.load(json_file)

        try:
            CATEGORIES = data["categories"]
        except Exception as exc:
            pass

        try:
            REMOVE_LINES = data["excludes"]["lines"]
        except Exception as exc:
            pass

        try:
            REMOVE_WORDS = data["excludes"]["words"]
        except Exception as exc:
            pass
except Exception as exc:
    pass


def cloc(string: str) -> int:
    """
    Counts the number of lines in a string.

    Arguments:
      string {str} - The string to count.

    Returns:
      {int} The number of lines.
    """
    return len(string.split("\n"))


def file_to_str(file_path: str) -> str:
    """
    Reads a file and returns it as a string.

    Arguments:
      file_path {str} - The path to the file.

    Returns:
      {str} The string representation of the file.
    """
    with open(file_path, "r", encoding="utf8") as file:
        read_str = file.read()

    return read_str


def str_to_file(write_str: str, file_path: str):
    """
    Writes a string to a file.

    Arguments:
      write_str {str} - The string to write to the file.
      file_path {str} - The path to the file to write to.
    """
    with open(file_path, "w", encoding="utf8") as file:
        file.write(write_str)


def optimize_whitespaces(string: str) -> str:
    """
    Removes extraneous whitespaces from each line of a string.

    Arguments:
      string {str} - The string to optimize.

    Returns:
      {str} The optimized string.
    """
    # Remove all blank lines.
    string = re.sub(r"(?imu)^\s*\n", r"", string)

    # Remove consecutive spaces.
    string = re.sub(r" +", " ", string)

    # Remove leading white spaces.
    string = re.sub(r"(\n) +", r"\1", string)

    # Remove trailing white spaces.
    string = re.sub(r" +(\n)", r"\1", string)

    # Convert tabs to spaces.
    string = re.sub(r"\t", " ", string)

    return string


def redact_lines(string: str) -> str:
    """
    Redacts all lines in a string according to the dictionary of lines to exclude and words to
    exclude.

    Arguments:
      string {str} - The string to redact.

    Returns:
      {str} - The redacted string.
    """
    # Remove unwanted lines.
    for regex in REMOVE_LINES:
        string = re.sub(
            re.compile("%s%s%s" % (r"(.*?)", regex, r"(.*?)\n")), "", string
        )

    # Remove unwanted words.
    for regex in REMOVE_WORDS:
        string = re.sub(re.compile(regex), "", string)

    return string


def append_category_eol(line: str, delimiter: str = " ") -> str:
    """
    Assigns a category to a line by referring to the JSON dictionary of CATEGORIES. If the category not
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
    """
    default_category = "Other"
    tmp_prefix = "<TMP>"
    line = re.sub(r"^(.*)$", rf"{tmp_prefix}\1", line)

    for category in CATEGORIES:
        for regex in CATEGORIES[category]:
            (line, subbed) = re.subn(
                re.compile(f"{tmp_prefix}{r'(.*?'}{regex}{r'.*?)$'}"),
                r"\1" + delimiter + category,
                line,
                1,
            )

            if subbed > 0:
                break
        if subbed > 0:
            break

    line = re.sub(rf"^{tmp_prefix}(.*)$", r"\1" + delimiter + default_category, line)

    return line
