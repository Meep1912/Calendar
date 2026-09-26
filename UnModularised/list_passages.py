"""One-off: show every passage's id, date and first line, so you can see what's wrong."""
import comprehension_db as db

with db.connection() as conn:
    rows = conn.execute("SELECT id, date, text FROM passages ORDER BY date").fetchall()

for r in rows:
    first_line = r["text"].strip().splitlines()[0][:40]
    print(f"id={r['id']:<4} date={r['date']}   {first_line}")

print(f"\n{len(rows)} passages total.")
