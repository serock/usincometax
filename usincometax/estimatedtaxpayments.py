#!/usr/bin/env python3

"""Estimated tax payments

Read quarterly estimated tax payments from a CSV file and write them to the console in Tax
Exchange Format (TXF).

The requirements of the CSV file are as follows:
    * The mandatory column names for federal tax payments are Date and Amount.
    * The mandatory column names for state tax payments are Date, Amount, and State.
    * Optional column names are Account, Check Number, Payee, Memo, and Category.
    * The first row must be a header row that contains the column names.
    * The last row must have the sum of all tax payments in the Amount column.
    * The last row must not have any values in the Date, Account, Check Number, Payee, Memo, or
      Category columns.
    * The State column must have a two character state abbreviation for state tax payments.
    * All of the values in the State column must be the same.
    * Date values must be in mm/dd/yyyy format, where the month and day have two digits
      (e.g., 01/01/2021).
    * All date values must be within the same tax year.
"""

from argparse import ArgumentParser
import csv
import sys
from typing import Dict
from typing import List
from typing import Mapping
from typing import Sequence
import taxexchangeformat

def read_tax_payments(csv_filename: str) -> List[Dict[str, str]]:
    """Read quarterly estimated tax payments from CSV file."""
    rows = []
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows.extend(reader)
    return rows

def write_txf_records(rows: Sequence[Mapping[str, str]], omit_header: bool) -> None:
    """Write quarterly estimated tax payments to console as TXF records."""
    if not omit_header:
        taxexchangeformat.write_header('usincometax 2020.0.0')
    if rows[0].get('State') is None:
        for row in rows:
            if row['Date'] == '':
                taxexchangeformat.write_federal_est_tax_summary(row['Amount'])
            else:
                taxexchangeformat.write_federal_est_tax_payment(
                    row['Date'],
                    row['Amount'],
                    row.get('Account', ''),
                    row.get('Check Number', ''),
                    row.get('Payee', ''),
                    row.get('Memo', ''),
                    row.get('Category', ''))
    else:
        for row in rows:
            if row['Date'] == '':
                taxexchangeformat.write_state_est_tax_summary(row['Amount'], row['State'])
            else:
                taxexchangeformat.write_state_est_tax_payment(
                    row['Date'],
                    row['Amount'],
                    row['State'],
                    row.get('Account', ''),
                    row.get('Check Number', ''),
                    row.get('Payee', ''),
                    row.get('Memo', ''),
                    row.get('Category', ''))
    return

def csv_to_txf(csv_filename: str, omit_header: bool) -> None:
    """Read quarterly estimated tax payments from a CSV file and write TXF records to the console.
    """
    rows = read_tax_payments(csv_filename)
    write_txf_records(rows, omit_header)
    return

def main() -> None:
    """Parse command line arguments and run."""
    parser = ArgumentParser(description='Generate Tax Exchange Format (TXF) records from a'\
        ' quarterly estimated tax payments CSV file')
    parser.add_argument('infile', nargs=1, help='a quarterly estimated tax payments CSV file')
    parser.add_argument(
        '-o', '--omit-header',
        action='store_true',
        help='omit the header record from the TXF output')
    args = parser.parse_args()
    csv_to_txf(args.infile[0], args.omit_header)
    return

if __name__ == '__main__':
    main()
    sys.exit()
