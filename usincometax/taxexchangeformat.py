"""Write tax data to the console in Tax Exchange Format (TXF)."""

import datetime
from typing import Optional

def _txf_write(*obj: str) -> None:
    # Write objects to the console with the recommended TXF line terminator.
    print(*obj, end='\r\n')
    return

def _txf_normalize_amount(amount: str) -> str:
    # Remove any '$' or ',' or '-' characters from the amount.
    amount = amount.translate({36: None, 44: None, 45: None})
    return '0' + amount if amount.startswith('.') else amount

def _txf_expense(amount: str) -> str:
    # Ensure that non-zero expense amounts are negative.
    amount = _txf_normalize_amount(amount)
    return amount if amount == '0.00' else '-' + amount

def _txf_income(amount: str) -> str:
    # Ensure that non-zero income amounts are positive.
    return _txf_normalize_amount(amount)

def _txf_write_record_format_1(
        amount: str, ref_num: int,
        copy: int = 1, line: int = 1, detail: Optional[str] = None) -> None:
    # Write a Record Format 1 TXF record.
    _txf_write('TS' if detail is None else 'TD')
    _txf_write(f'N{ref_num}')
    _txf_write(f'C{copy}')
    _txf_write(f'L{line}')
    _txf_write('$' + amount)
    if detail is not None:
        _txf_write('X' + detail)
    _txf_write('^')
    return

def _txf_write_record_format_3(
        amount: str, description: str, ref_num: int,
        copy: int = 1, line: int = 1, detail: Optional[str] = None) -> None:
    # Write a Record Format 3 TXF record.
    _txf_write('TS' if detail is None else 'TD')
    _txf_write(f'N{ref_num}')
    _txf_write(f'C{copy}')
    _txf_write(f'L{line}')
    _txf_write('$' + amount)
    _txf_write('P' + description)
    if detail is not None:
        _txf_write('X' + detail)
    _txf_write('^')
    return

def _txf_write_record_format_6(
        date: str, amount: str, state: str, ref_num: int, copy: int = 1,
        line: int = 1, detail: Optional[str] = None) -> None:
    # Write a Record Format 6 TXF record.
    _txf_write('TS' if detail is None else 'TD')
    _txf_write(f'N{ref_num}')
    _txf_write(f'C{copy}')
    _txf_write(f'L{line}')
    _txf_write('D' + date)
    _txf_write('$' + amount)
    _txf_write('P' + state)
    if detail is not None:
        _txf_write('X' + detail)
    _txf_write('^')
    return

def write_header(program: str) -> None:
    """Write a TXF header."""
    _txf_write('V042')
    _txf_write('A' + program)
    _txf_write('D' + datetime.date.today().strftime('%m/%d/%Y'))
    _txf_write('^')
    return

def write_1099int(payer: str, box_1: str = None, box_3: str = None, box_4: str = None) -> None:
    """Write TXF records for a Form 1099-INT."""
    if box_1 is not None:
        _txf_write_record_format_3(_txf_income(box_1), payer, 287)
    if box_3 is not None:
        _txf_write_record_format_3(_txf_income(box_3), payer, 288)
    if box_4 is not None:
        _txf_write_record_format_3(_txf_expense(box_4), payer, 616)
    return

def write_cash_donation(
        date: str, payee: str, amount: str, account: str, check_number: str, memo: str,
        category: str) -> None:
    """Write a TXF detail record for a cash donation."""
    # Ensure that a category is present so that TurboTax will parse the detail line correctly.
    if category.lstrip() == '':
        category = 'Cash donation'
    _txf_write_record_format_1(
        _txf_expense(amount), 280,
        detail=f'{date:10.10} {account:30.30} {check_number:6.6} {payee:40.40}'\
            f'{memo:40.40} {category:.15}')
    return

def write_cash_donations_summary(amount: str) -> None:
    """Write a TXF summary record for cash donations."""
    _txf_write_record_format_1(_txf_expense(amount), 280)
    return

def write_federal_est_tax_payment(
        date: str, amount: str, account: str, check_number: str, payee: str, memo: str,
        category: str) -> None:
    """Write a TXF detail record for a federal quarterly estimated tax payment."""
    # Ensure that a category is present so that TurboTax will parse the detail line correctly.
    if category.lstrip() == '':
        category = 'Fed qtr est tax'
    _txf_write_record_format_6(
        date, _txf_expense(amount), 'XX', 521,
        detail=f'{date:10.10} {account:30.30} {check_number:6.6} {payee:40.40}'\
            f'{memo:40.40} {category:.15}')
    return

def write_federal_est_tax_summary(amount: str) -> None:
    """Write a TXF summary record for federal quarterly estimated tax payments."""
    _txf_write_record_format_6('', _txf_expense(amount), 'XX', 521)
    return

def write_state_est_tax_payment(
        date: str, amount: str, state: str, account: str, check_number: str, payee: str,
        memo: str, category: str) -> None:
    """Write a TXF detail record for a state quarterly estimated tax payment."""
    # Ensure that a category is present so that TurboTax will parse the detail line correctly.
    if category.lstrip() == '':
        category = 'Sta qtr est tax'
    _txf_write_record_format_6(
        date, _txf_expense(amount), state, 522,
        detail=f'{date:10.10} {account:30.30} {check_number:6.6} {payee:40.40}'\
            f'{memo:40.40} {category:.15}')
    return

def write_state_est_tax_summary(amount: str, state: str) -> None:
    """Write a TXF summary record for state quarterly estimated tax payments."""
    _txf_write_record_format_6('', _txf_expense(amount), state, 522)
    return
