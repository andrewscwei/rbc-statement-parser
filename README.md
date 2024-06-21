# RBC Statement Parser

Python script for parsing RBC PDF statements, compatible with both VISA and personal banking accounts (i.e. chequing, savings, etc). The output is a list of formatted transactions printed on console or output to a file.

## Setup

Set up environment:

```sh
$ pre-commit install
$ pipenv install -d
$ pipenv shell
```

## Usage

Download PDF statements from RBC and save them in a directory.

```sh
# Parse PDF(s) and output to console
$ python main.py <pdf_file_or_dir_of_pdf_files>

# Parse PDF(s) and output to console and out.txt
$ python main.py <pdf_file_or_dir_of_pdf_files> -o out.txt
```

## Linting

```sh
$ pylint **/*.py
```

## Config

Create a `.rc` file in project root. You can also provide another file name and pass it to `--config` or `-c` option flag when executing `main.py`. See below example to understand what this config does:

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
