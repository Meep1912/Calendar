"""One-off: fix wrong dates by passage id.

1. Run list_passages.py first to find the ids of the wrong entries.
2. Fill in FIXES below: {id: "correct date"}.
3. Run this script. It shows what it's about to do and asks before touching anything.
"""
import comprehension_db as db

FIXES = {
    # passage_id: "2026-10-27",
    # passage_id: "2026-10-28",
    8:"2026-9-27",
    9:"2026-9-28",
    10:"2026-9-29",
}


def main():
    if not FIXES:
        print("FIXES is empty. Open this file and fill in {id: 'correct date'} pairs.")
        return

    with db.connection() as conn:
        rows = {r["id"]: r for r in conn.execute("SELECT id, date, text FROM passages")}

    print("About to change:")
    for pid, new_date in FIXES.items():
        if pid not in rows:
            print(f"  id={pid}: NOT FOUND, skipping")
            continue
        old = rows[pid]
        try:
            iso = db.parse_date(new_date)
        except ValueError as e:
            print(f"  id={pid}: bad date {new_date!r} ({e}), skipping")
            continue
        first_line = old["text"].strip().splitlines()[0][:40]
        print(f"  id={pid}: {old['date']} -> {iso}   ({first_line})")

    if input("\nType 'yes' to apply: ").strip().lower() != "yes":
        print("Cancelled, nothing changed.")
        return

    with db.connection() as conn:
        for pid, new_date in FIXES.items():
            if pid not in rows:
                continue
            try:
                iso = db.parse_date(new_date)
            except ValueError:
                continue    # already reported above
            clash = conn.execute(
                "SELECT id FROM passages WHERE date = ? AND id <> ?", (iso, pid)).fetchone()
            if clash:
                print(f"  id={pid}: SKIPPED, {iso} is already used by id={clash['id']}")
                continue
            conn.execute("UPDATE passages SET date = ? WHERE id = ?", (iso, pid))
            print(f"  id={pid}: done")

    print("\nFinished. Run list_passages.py again to check.")


if __name__ == "__main__":
    main()
