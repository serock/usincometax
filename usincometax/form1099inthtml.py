#!/usr/bin/env python3

"""Form 1099-INT HTML

Extract Payer Name, Box 3 data, and Box 4 data from a Treasury Direct Form 1099-INT HTML file
and write the data to the console in Tax Exchange Format (TXF).
"""

from argparse    import ArgumentParser
from html.parser import HTMLParser
import sys
import taxexchangeformat

class TreasuryDirectHtmlParser(HTMLParser):
    """HTML parser for Treasury Direct Form 1099-INT."""
    box_3 = None
    box_4 = None
    done = False
    found_1099_int = False
    found_payer_info = False
    found_1099_int_totals = False
    payer_name = None

    def _handle_payer(self, data: str) -> bool:
        if data == "Payer Information:":
            self.found_payer_info = True
            return True
        if self.payer_name is None and self.found_payer_info:
            self.payer_name = data.strip()
            return True
        return False

    def _handle_totals(self, data: str) -> None:
        if data == "Totals:" and self.found_1099_int:
            self.found_1099_int_totals = True
            return
        if self.found_1099_int_totals:
            if self.box_3 is None:
                if data.startswith('$'):
                    self.box_3 = data
                    return
            if self.box_4 is None:
                if data.startswith('$'):
                    self.box_4 = data
                    self.done = True
                    return
        return

    def handle_data(self, data: str) -> None:
        """Cache relevant data."""
        if self.done:
            return
        if self._handle_payer(data):
            return
        if data.startswith('Form 1099-INT'):
            self.found_1099_int = True
            return
        self._handle_totals(data)
        return

    def get_payer_name(self) -> str:
        """Return the payer of the interest."""
        return self.payer_name

    def get_savings_bonds_interest(self) -> str:
        """Return the savings bonds interest from box 3."""
        return self.box_3

    def get_federal_tax_withheld(self) -> str:
        """Return the federal tax withheld from box 4."""
        return self.box_4

def parse_file(filename: str, parser: TreasuryDirectHtmlParser) -> None:
    """Parse the HTML file and cache extracted within the parser."""
    with open(filename, mode='r', encoding='windows-1252') as html_file:
        data = html_file.read()
        parser.feed(data)
    return

def html_to_txf(filename: str, omit_header: bool) -> None:
    """Read interest income data from an HTML file and write TXF records to the console."""
    html_parser = TreasuryDirectHtmlParser()
    parse_file(filename, html_parser)
    if not omit_header:
        taxexchangeformat.write_header('usincometax 2020.0.0')
    taxexchangeformat.write_1099int(
        payer=html_parser.get_payer_name(),
        box_3=html_parser.get_savings_bonds_interest(),
        box_4=html_parser.get_federal_tax_withheld())
    return

def main() -> None:
    """Parse command line arguments and run."""
    parser = ArgumentParser(
        description='Generate Tax Exchange Format (TXF) records from a 1099-INT HTML file')
    parser.add_argument('infile', nargs=1, help='a 1099-INT HTML file from TreasuryDirect')
    parser.add_argument(
        '-o', '--omit-header',
        action='store_true',
        help='omit the header record from the TXF output')
    args = parser.parse_args()
    html_to_txf(args.infile[0], args.omit_header)
    return

if __name__ == '__main__':
    main()
    sys.exit()
