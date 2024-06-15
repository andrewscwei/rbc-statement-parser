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
$ python parse_chq.py <path-to-txt-file-of-chequing-savings-transactions-copied-from-pdf>
$ python parse_visa.py <path-to-txt-file-of-visa-transactions-copied-from-pdf>
```

## Document Setup

Only the following use cases are supported. For any other uses cases this script will not work.

### Visa Statements in PDF Format

1. Download the statement as a PDF
2. Upload it to your Google Drive
3. Open the PDF **from within** Google Drive on your browser
4. Copy the transaction rows with the selection caret starting at the first character of the date of the first transaction, and ending at the last character of the money amount of the last statement (page breaks are not accounted for, so copy the statements in the table PER PAGE)
5. Paste these rows into a **new line** of a text file

The text file is now ready to be parsed by `parse_visa.py`.

> **WARNING**: You need to do the above exactly as described. Meaning you have to open the PDF from Google Drive and copy the rows to your clipboard from inside the PDF file opened by Google Drive. This is because rows copied by Google Drive has a specific format that is favorable and different from that of other programs. If you copy the rows from another program, say, _macOS Preview_, this script will not work.

### Personal Banking Statements in PDF Format

This includes accounts such as chequing and savings, where you can deposit/withdraw money from.

1. Download the statement as a PDF
2. Upload it to your Google Drive
3. Open the PDF **from within** Google Drive on your browser
4. Copy the transaction rows with the selection caret starting at the first character of the date of the first transaction, and ending at the last character of the money amount of the last statement (page breaks are not accounted for, so copy the statements in the table PER PAGE)
5. Paste these rows into a **new line** of a text file.

The text file is now ready to be parsed by `parse_chq.py`.

> **WARNING**: You need to do the above exactly as described. Meaning you have to open the PDF from Google Drive and copy the rows to your clipboard from inside the PDF file opened by Google Drive. This is because rows copied by Google Drive has a specific format that is favorable and different from that of other programs. If you copy the rows from another program, say, _macOS Preview_, this script will not work.

## Defining Categories and Excluding Specific Transactions

Create a `.config` file in project root. This file serves as a lookup JSON file for defining transaction categories and excluding certain transactions from being parsed by matching them with specific lines or keywords. The format is as follows:

```json
{
  "categories": {
    "<category_1_name>": [
      "<transaction_keywords>",
      "<transaction_keywords>",
      "<transaction_keywords>",
      ...
    ],
    "<category_2_name>": [
      "<transaction_keywords>",
      "<transaction_keywords>",
      "<transaction_keywords>",
      ...
    ],
    ...
  },
  "excludes": {
    "lines": [
    "<some_line_of_text>",
    "<some_line_of_text>",
    ...
    ],
    "words": [
      "<some_keyword>",
      "<some_keyword>",
      ...
    ]
  }
}
```

## Caveats

When parsing chequing or savings statements, the script cannot identify whether the amount is credited or debited. You'll have to manually make adjustments.

## Disclaimer

This script only works for **VERY SPECIFIC** cases.
