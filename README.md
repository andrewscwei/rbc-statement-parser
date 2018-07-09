# rbc-visa-statement-parser

Handy Python script to parse RBC Visa statements and outputs a file that contains columns: **Transaction Date**, **Activity Description** and **Amount**.

## Usage

This script only works under very specific conditions:

1. You downloaded the RBC Visa statement as a PDF file and uploaded it onto Google Drive
2. Using Google Drive's PDF viewer, you copied each transaction row of the statement to the clipboard. You can bulk copy muliple rows, but you **MUST ONLY** copy the contents of the transaction rows, nothing else.
3. Paste everything to some text editor.
4. Repeat for all statements you have.
5. Save the file somewhere locally.

Next, simply run:

```sh
$ python parse.py <PATH_TO_FILE>
```

Voila, your statements are parsed into 3 columns: **Transaction Date**, **Activity Description** and **Amount**. You can then bulk copy them to Google Sheets.

## Disclaimer

This script only works for **VERY SPECIFIC** cases.

## License

This software is released under the [MIT License](http://opensource.org/licenses/MIT).