#!/usr/bin/env python3

"""Form 1099-INT PDF

Extract Payer Name and Box 1 data from a Form 1099-INT PDF file and write the data to the
console in Tax Exchange Format (TXF). The 1099-INT PDF must have the same layout as the
Form 1099-INT, Copy B For Recipient, at https://www.irs.gov/pub/irs-pdf/f1099int.pdf.
"""
# TODO switch to the pdfminer high-level extract_pages API after upgrading
# pdfminer.six dependency to version 20200720 or higher

from argparse           import ArgumentParser
import sys
from typing             import List
from typing             import Optional
from typing             import Sequence
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout    import LAParams
from pdfminer.layout    import LTTextBoxHorizontal
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage   import PDFPage
import taxexchangeformat

def get_text_boxes(filename: str, page: int = 1) -> List[LTTextBoxHorizontal]:
    """Return the horizontal text boxes on the PDF page."""
    resource_manager = PDFResourceManager(caching=True)
    layout_analysis_params = LAParams(char_margin=1.4, line_margin=0.01)
    device = PDFPageAggregator(resource_manager, laparams=layout_analysis_params)
    interpreter = PDFPageInterpreter(resource_manager, device)
    with open(filename, mode='rb') as pdf_file:
        page_generator = PDFPage.get_pages(
            pdf_file,
            pagenos=[page-1],
            maxpages=1,
            check_extractable=False)
        for pdf_page in page_generator:
            interpreter.process_page(pdf_page)
            layout_page = device.get_result()
            text_boxes = []
            for child in layout_page:
                if isinstance(child, LTTextBoxHorizontal):
                    text_boxes.append(child)
    return text_boxes

def _get_form_text_box(
        text_boxes: Sequence[LTTextBoxHorizontal], with_text: str) -> LTTextBoxHorizontal:
    for text_box in text_boxes:
        if text_box.get_text() == with_text:
            return text_box
    raise ValueError(with_text)

def _is_east(text_box: LTTextBoxHorizontal, text_box_e: LTTextBoxHorizontal) -> bool:
    """Return True if the left edge of text_box_e is east of the right edge of text_box."""
    return text_box_e.x0 > text_box.x1

def _is_northwest(text_box: LTTextBoxHorizontal, text_box_nw: LTTextBoxHorizontal) -> bool:
    """Return True if the left edge of text_box_nw is west of the left edge of text_box and the
    bottom edge of text_box_nw is north of the top edge of text_box.
    """
    return text_box_nw.x0 < text_box.x0 and text_box_nw.y0 > text_box.y1

def _is_south(text_box: LTTextBoxHorizontal, text_box_s: LTTextBoxHorizontal) -> bool:
    """Return True if the top edge of text_box_s is south of the bottom edge of text_box."""
    return text_box_s.y1 < text_box.y0

def _get_trimmed_text(text_box: LTTextBoxHorizontal) -> str:
    return text_box.get_text().rstrip('\n')

def find_payer_name_data(text_boxes: Sequence[LTTextBoxHorizontal]) -> Optional[str]:
    """Return the payer name or None if not found."""
    form_text_box_northwest = _get_form_text_box(
        text_boxes,
        with_text='or foreign postal code, and telephone no.\n')
    form_text_box_south = _get_form_text_box(text_boxes, with_text='PAYER’S TIN\n')
    form_text_box_east = _get_form_text_box(text_boxes, with_text='10 Market discount\n')
    for text_box in text_boxes:
        if _is_northwest(text_box, form_text_box_northwest) and\
            _is_south(text_box, form_text_box_south) and _is_east(text_box, form_text_box_east):
            return _get_trimmed_text(text_box)
    return None

def find_box_1_data(text_boxes: Sequence[LTTextBoxHorizontal]) -> Optional[str]:
    """Return the interest income from box 1 or None if not found."""
    form_text_box_northwest = _get_form_text_box(text_boxes, with_text='1 Interest income\n')
    form_text_box_south = _get_form_text_box(text_boxes, with_text='2 Early withdrawal penalty\n')
    form_text_box_east = _get_form_text_box(text_boxes, with_text='11 Bond premium\n')
    for text_box in text_boxes:
        if _is_northwest(text_box, form_text_box_northwest) and\
            _is_south(text_box, form_text_box_south) and _is_east(text_box, form_text_box_east):
            return _get_trimmed_text(text_box)
    return None

def pdf_to_txf(filename: str, omit_header: bool) -> None:
    """Read interest income data from a PDF file and write TXF records to the console."""
    text_boxes = get_text_boxes(filename)
    payer_name = find_payer_name_data(text_boxes)
    interest_income = find_box_1_data(text_boxes)
    if not omit_header:
        taxexchangeformat.write_header('usincometax 2020.0.0')
    taxexchangeformat.write_1099int(payer=payer_name, box_1=interest_income)
    return

def main() -> None:
    """Parse command line arguments and run."""
    parser = ArgumentParser(
        description='Generate Tax Exchange Format (TXF) records from a 1099-INT PDF file')
    parser.add_argument('infile', nargs=1, help='a 1099-INT PDF file')
    parser.add_argument(
        '-o', '--omit-header',
        action='store_true',
        help='omit the header record from the TXF output')
    args = parser.parse_args()
    pdf_to_txf(args.infile[0], args.omit_header)
    return

if __name__ == '__main__':
    main()
    sys.exit()
