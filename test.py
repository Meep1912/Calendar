import json
from datetime import date, datetime, timedelta


start = date(2025, 1, 1)
end = date(2026, 12, 31)

all_dates = {}
current = start
while current <= end:
    all_dates[
        f"{current.day:02d}|{current.month:02d}|{current.year}"
        ] = []
    current += timedelta(days=1)
with open("Days.json","w") as f:
    days_json = json.dump(all_dates,f,indent=4)

