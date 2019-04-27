# rbc-statement-parser

Handy Python script to parse RBC statements and outputs a file that contains columns: **Transaction Date**, **Activity Description** and **Amount**.

## Setup

Use [VSCode](https://code.visualstudio.com/) with [Python extension](https://marketplace.visualstudio.com/itemdetails?itemName=ms-python.python). This project also uses [mypy](http://mypy-lang.org/) as its Python linter, so be sure to enable the following in `.vscode/settings.json`:

```json
{
  ...
  "python.linting.pylintEnabled": false,
  "python.linting.mypyEnabled": true,
  "python.linting.enabled": true,
  ...
}
```

## Usage

This script only works under very specific conditions:

1. From Online Banking (or from Visa statement PDF), you copied all transaction rows to the clipboard. You can bulk copy muliple rows, but you **MUST ONLY** copy the contents of the transaction rows, nothing else.
2. Paste everything to some text editor.
3. Repeat for all statements you have.
4. Save the file somewhere locally.

Next, simply run:

```sh
$ pipenv install
$ pipenv shell
$ python parse.py <PATH_TO_FILE>
```

Voila, your statements are parsed into 4 columns: **Transaction Date**, **Activity Description**, **Amount** and **Reference Code**. You can then bulk copy them to Google Sheets.

## Disclaimer

This script only works for **VERY SPECIFIC** cases.
