import json

from datetime import date, timedelta


start = date(2025, 1, 1)
end = date(2026, 12, 31)

all_dates = {}

current = start

while current <= end:

    all_dates[
        f"{current.day:02d}|{current.month:02d}|{current.year}"
    ] = {
        "text": "",
        "questions": [],
        "correct_answer":[],
        "given_answer":[],
    }

    current += timedelta(days=1)


with open("Comprehension.json", "w") as f:
    json.dump(all_dates, f, indent=4)

