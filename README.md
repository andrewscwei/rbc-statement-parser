# RBC Statement Parser

Python script for parsing RBC PDF statements, compatible with both VISA and personal banking accounts (i.e. chequing, savings, etc). The output is a list of formatted transactions printed on console or output to a file.

## Usage

Download PDF statements from RBC and save them in a directory.

```sh
# Parse PDF(s) and output to console
$ python main.py <pdf_file_or_dir_of_pdf_files>

# Parse PDF(s) and output to console and out.txt
$ python main.py <pdf_file_or_dir_of_pdf_files> -o out.txt
```

## Requirements

- **Python**
  - Version number specified in `./python-version`)

- **Python Pip packages**
  - `pipenv`

- **Optional**
  - Docker
  - pre-commit

## Install

### Quick Install

In Terminal:

```shell
pipenv install --python $(which python3) -d
pipenv shell
```

### Full Install

```shell
# Clone the repo
git clone https://github.com/andrewscwei/rbc-statement-parser.git
cd rbc-statement parser

# Install pipenv if it doesn't exist
if ! command -v pipenv >/dev/null 2>&1; then
    echo "Installing pipenv..."
    if command -v pipx >/dev/null 2>&1; then
      pipx install --no-cache-dir pipenv
    else
      pip install --user pipenv
    fi
fi

pipenv install --python $(which python3) -d
pipenv shell

python main.py /path/to/your/pdf-files
```

## Config File

The parser will look for a `.rc` config file in the project root. If no file is found, the parser will use a default config.

To create your own custom config, see `.rcexample` for a template.

To provide a custom config file name or path, use the `--config` or `-c` option flag when executing `main.py`. 
Example: `python main.py --config /path/to/myRcFile`

### `.rc` file structure

```js
{
  // String format of each transaction in the output, the following is the
  // default.
  "format": "{date}\t{method}\t{code}\t{description}\t{category}\t{amount}",

  // Each key is a category name to be assigned to a parsed transaction, and
  // each array element is a regex pattern where if the transaction description
  // matches any of the patterns, the category association will be made.
  "categories": {
    "<category_1_name>": [
      "<pattern_1>",
      "<pattern_2>",
      "<pattern_3>",
      ...
    ],
    "<category_2_name>": [
      "<pattern_1>",
      "<pattern_2>",
      "<pattern_3>",
      ...
    ],
    ...
  },
  // Each array element is a regex pattern where if the transaction description
  // matches any of the patterns, it will be excluded from the output.
  "excludes": [
    "<pattern_1>",
    "<pattern_2>",
    "<pattern_3>",
    ...
  ]
}
```

## Docker Usage

This project can also be built and ran inside a Docker container:

```shell
cd rbc-statement-parser

docker build -t rbc-parser .

alias rbcparser='docker run --rm -v "$(pwd)":/app/input -v "$(pwd)":/app/output rbc-parser /app/input/ -o /app/output/output-$(date +"%s").txt'

cd /path/to/your/rbc-pdf-files/

# Parse all PDFs in current diretory into a output.txt file:
rbcparser
```

## Linting

```sh
pre-commit install
pylint **/*.py
```
