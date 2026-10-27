import json
from datetime import date, timedelta

def date_dict(start, end):
    """Return a dict with 'YYYY|MM|DD' keys (start to end, inclusive) and empty list values."""
    result = {}
    current = start
    while current <= end:
        result[current.strftime("%d|%m|%Y")] = []
        current += timedelta(days=1)
    return result


dates = date_dict(date(2025, 1, 1), date(2050, 12, 30))

with open("Days.json", "w", encoding="utf-8") as f:
        json.dump(dates, f, indent=4)