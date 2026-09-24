
from datetime import date, timedelta
import json

start = date(2026, 9, 16)
end = date(2026, 9, 24)

current = start

new_dict = {}
i = 1

with open("Comprehension copy.json", "r", encoding="utf-8") as f:
    all_dates = json.load(f)

while current <= end:

    key = f"{current.day:02d}|{current.month:02d}|{current.year}"

    data_at_that_day = all_dates[key]

    new_dict[i] = data_at_that_day

    i += 1
    current += timedelta(days=1)

with open("Comprehension.json", "w", encoding="utf-8") as f:
    json.dump(
        new_dict,
        f,
        indent=4,
        ensure_ascii=False
    )


all_numbers = {}
for i in range(0,100):
    all_numbers[i] = {
        "text":"",
        "questions":"",
        "correct_answer":"",
        "given_answer":"",
        "struggled":"",
    }

#with open("Comprehension.json", "w", encoding="utf-8") as f:
    json.dump(
        all_numbers,
        f,
        indent=4,
        ensure_ascii=False
    )