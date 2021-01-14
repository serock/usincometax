#!/usr/bin/env python3

"""Cash donations

Read cash donations from a CSV file and write them to the console in Tax Exchange Format (TXF).

The requirements of the CSV file are as follows:
    * The mandatory column names are Date, Payee, and Amount.
    * Optional column names are Account, Check Number, Memo, and Category.
    * The first row must be a header row that contains the column names.
    * The last row must have the sum of all cash donations in the Amount column.
    * The last row must not have any values in the Date, Payee, Account, Check Number, Memo, or
      Category columns.
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

def _replace_dates(rows: Sequence[Mapping[str, str]]) -> None:
    # Replace the date in each row with 'Various'.
    for row in rows:
        row['Date'] = 'Various'
    return

def _map_rows_to_payees(rows: Sequence[Mapping[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    # Return a mapping of payees to rows.
    rows_for_payees = {}
    for row in rows:
        payee = row['Payee']
        if payee is not None and payee not in rows_for_payees:
            rows_for_payees[payee] = []
        rows_for_payees[payee].append(row)
    return rows_for_payees

def _replace_different_dates(rows_for_payees: Mapping[str, Sequence[Mapping[str, str]]]) -> None:
    # Determine if there are multiple dates for a payee; if true, replace those dates with
    # 'Various'.
    for payee in list(rows_for_payees):
        payee_rows = rows_for_payees[payee]
        if len(payee_rows) > 1:
            last_date = payee_rows[-1]['Date']
            for payee_row in payee_rows:
                if payee_row['Date'] != last_date:
                    _replace_dates(payee_rows)
                    break
    return

def read_cash_donations(csv_filename: str, replace_dates: bool) -> List[Dict[str, str]]:
    """Read cash donations from CSV file."""
    rows = []
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows.extend(reader)
    if replace_dates:
        rows_for_payees = _map_rows_to_payees(rows)
        _replace_different_dates(rows_for_payees)
    return rows

def write_txf_records(rows: Sequence[Mapping[str, str]], omit_header: bool) -> None:
    """Write cash donations to console as TXF records."""
    if not omit_header:
        taxexchangeformat.write_header('usincometax 2020.0.0')
    for row in rows:
        if row['Date'] == '':
            taxexchangeformat.write_cash_donations_summary(row['Amount'])
        else:
            taxexchangeformat.write_cash_donation(
                row['Date'],
                row['Payee'],
                row['Amount'],
                row.get('Account', ''),
                row.get('Check Number', ''),
                row.get('Memo', ''),
                row.get('Category', ''))
    return

def csv_to_txf(csv_filename: str, replace_dates: bool, omit_header: bool) -> None:
    """Read cash donations from a CSV file and write TXF records to the console."""
    rows = read_cash_donations(csv_filename, replace_dates)
    write_txf_records(rows, omit_header)
    return

def main() -> None:
    """Parse command line arguments and run."""
    parser = ArgumentParser(
        description='Generate Tax Exchange Format (TXF) records from a cash donations CSV file')
    parser.add_argument('infile', nargs=1, help='a cash donations CSV file')
    parser.add_argument(
        '-o', '--omit-header',
        action='store_true',
        help='omit the header record from the TXF output')
    parser.add_argument(
        '-r', '--replace-dates',
        action='store_true',
        help='replace different dates with Various')
    args = parser.parse_args()
    csv_to_txf(args.infile[0], args.replace_dates, args.omit_header)
    return

if __name__ == '__main__':
    main()
    sys.exit()
