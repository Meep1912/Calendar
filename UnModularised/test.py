import json
from datetime import date, timedelta


with open("Comprehension.json", "r", encoding="utf-8") as f:
    all_dates = json.load(f)


start = date(2025, 1, 1)
end = date(2026, 12, 31)

current = start

while current <= end:

    key = f"{current.day:02d}|{current.month:02d}|{current.year}"

    if key not in all_dates:
        all_dates[key] = {
            "text": "",
            "questions": [],
            "correct_answer": [],
            "given_answer": [],
        }

    current += timedelta(days=1)


with open("Comprehension.json", "w", encoding="utf-8") as f:
    json.dump(
        all_dates,
        f,
        indent=4,
        ensure_ascii=False
    )
