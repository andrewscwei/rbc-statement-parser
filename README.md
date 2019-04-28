# rbc-statement-parser

Handy Python scripts for parsing copied and pasted RBC PDF statements, compatible with both VISA and personal banking accounts (i.e. chequing, savings, etc.). The output is a file separated by columns such as **Transaction Date**, **Description**, **Amount**, **Purchase Category**, etc.

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

## Preparing Documents for Parsing

Only the following scenarios are supported. For any other scenario this script will not work.

### VISA Statements in PDF Format

Download the statement as a PDF, then upload it to your Google Drive. Open the PDF **from within** Google Drive on your browser, then copy the transaction rows with the selection caret starting at the first character of the date of the first transaction, and ending at the last character of the money amount of the last statement. Page breaks are not accounted for, so copy the statements in the table PER PAGE. Paste these rows into a **new line** of a text file. The text file is now ready to be parsed by `parse-raw.py`.

> **WARNING**: You need to do the above exactly as described. Meaning you have to open the PDF from Google Drive and copy the rows to your clipboard from inside the PDF file opened by Google Drive. This is because rows copied by Google Drive has a specific format that is favorable and different from that of other programs. If you copy the rows from another program, say, *macOS Preview*, this script will not work.

### VISA Statements Inside Online Banking

This refers to viewing your transactions from RBC Online Banking in a web browser. Simply copy the rows to a text file. They should be delimited by a tab. Run `parse-raw.py` against it.

### Personal Banking Statements in PDF Format

This includes accounts such as chequing and savings, where you can deposit/withdraw money from. Download the statement as a PDF, then upload it to your Google Drive. Open the PDF **from within** Google Drive on your browser, then copy the transaction rows with the selection caret starting at the first character of the date of the first transaction, and ending at the last character of the money amount of the last statement. Page breaks are not accounted for, so copy the statements in the table PER PAGE. Paste these rows into a **new line** of a text file. The text file is now ready to be parsed by `parse-pb-pdf.py`.

> **WARNING**: You need to do the above exactly as described. Meaning you have to open the PDF from Google Drive and copy the rows to your clipboard from inside the PDF file opened by Google Drive. This is because rows copied by Google Drive has a specific format that is favorable and different from that of other programs. If you copy the rows from another program, say, *macOS Preview*, this script will not work.

### Personal Banking Statements Inside Online Banking

Same as [VISA Statements Inside Online Banking](#visa-statements-inside-online-banking).

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
$ python parse-visa.py <PATH_TO_FILE>
```

Voila, your statements are parsed into 4 columns: **Transaction Date**, **Activity Description**, **Amount** and **Reference Code**. You can then bulk copy them to Google Sheets.

## Disclaimer

This script only works for **VERY SPECIFIC** cases.
