# RBC Statement Parser

Python scripts for parsing copied and pasted RBC PDF statements, compatible with both VISA and personal banking accounts (i.e. chequing, savings, etc.). The output is a file separated by columns such as **Transaction Date**, **Description**, **Amount**, **Purchase Category**, etc.

## Usage

Set up environment:

```sh
$ pyenv install
$ pipenv install
$ pipenv shell
```

Parse files:

```
$ python parse_csv.py <path-to-csv-file>
$ python parse_pdf.py <path-to-txt-file-of-transactions-copied-from-pdf>
$ python parse_tbl.py <path-to-txt-file-of-transactions-copied-from-online-banking>
```

## Document Setup

Only the following use cases are supported. For any other uses cases this script will not work.

### Visa Statements in PDF Format

1. Download the statement as a PDF
2. Upload it to your Google Drive
3. Open the PDF **from within** Google Drive on your browser
4. Copy the transaction rows with the selection caret starting at the first character of the date of the first transaction, and ending at the last character of the money amount of the last statement (page breaks are not accounted for, so copy the statements in the table PER PAGE)
5. Paste these rows into a **new line** of a text file

The text file is now ready to be parsed by `parse_tbl.py`.

> **WARNING**: You need to do the above exactly as described. Meaning you have to open the PDF from Google Drive and copy the rows to your clipboard from inside the PDF file opened by Google Drive. This is because rows copied by Google Drive has a specific format that is favorable and different from that of other programs. If you copy the rows from another program, say, *macOS Preview*, this script will not work.

### Personal Banking Statements in PDF Format

This includes accounts such as chequing and savings, where you can deposit/withdraw money from.

1. Download the statement as a PDF
2. Upload it to your Google Drive
3. Open the PDF **from within** Google Drive on your browser
4. Copy the transaction rows with the selection caret starting at the first character of the date of the first transaction, and ending at the last character of the money amount of the last statement (page breaks are not accounted for, so copy the statements in the table PER PAGE)
5. Paste these rows into a **new line** of a text file.

The text file is now ready to be parsed by `parse_pdf.py`.

> **WARNING**: You need to do the above exactly as described. Meaning you have to open the PDF from Google Drive and copy the rows to your clipboard from inside the PDF file opened by Google Drive. This is because rows copied by Google Drive has a specific format that is favorable and different from that of other programs. If you copy the rows from another program, say, *macOS Preview*, this script will not work.

### ~~Visa/Personal Banking Statements in CSV Format~~

> **DEPRECATED**: It doesn't seem like you can easily export CSV files now.

RBC now supports downloading statements as CSV files, delimited by `,`. Simply run `parse_csv.py` against them.

### ~~Visa/Personal Banking Statements Copied From Online Banking~~

> **DEPRECATED**: This no longer works because RBC changed its page layout. This method shouldn't be used at all since it is too tightly coupled with the page layout which is subject to change frequently.

This refers to viewing your transactions from RBC Online Banking in a web browser. Simply copy the rows to a text file. They should be delimited by a tab (`\t`). Run `parse_tbl.py` against it.

## Disclaimer

This script only works for **VERY SPECIFIC** cases.
