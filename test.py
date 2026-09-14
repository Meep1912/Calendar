import json
from datetime import date, datetime, timedelta


start = date(2025,1,1)
end = date(2026, 12, 31)

all_dates = []
current = start

with open("Days.json","r") as f:
    loaded = json.load(f)



while current <= end:
    all_dates.append({
        "year": current.year,
        "month": current.month,
        "day": current.day,
        "events": []
    })
    current += timedelta(days=1)

with open("Days.json","w") as f:
    json.dump(all_dates,f,indent=4)
