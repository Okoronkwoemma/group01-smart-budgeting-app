import re
import datetime

def parse_csv_line(line):
    """
    Parse a CSV line with regex to extract date, amount, category, description.
    Expected format: date, amount, category, description (description optional)
    Date format: YYYY-MM-DD or MM/DD/YYYY
    Amount: decimal number, can be negative
    """
    # Regex pattern to capture date, amount, category, description
    pattern = re.compile(
        r'\s*(?P<date>\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})\s*,\s*'  # date
        r'(?P<amount>-?\d+(?:\.\d+)?)\s*,\s*'  # amount
        r'(?P<category>[^,]+)\s*'  # category
        r'(?:,\s*(?P<description>.*))?'  # optional description
    )
    match = pattern.match(line)
    if not match:
        raise ValueError(f"Line does not match expected format: {line}")

    date_str = match.group('date')
    # Normalize date
    if '/' in date_str:
        date = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
    else:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    amount = float(match.group('amount'))
    category = match.group('category').strip()
    description = match.group('description') or ""

    return date, amount, category, description
