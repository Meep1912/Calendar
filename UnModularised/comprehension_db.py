"""All comprehension storage lives here. The UI only calls these functions."""
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comprehension.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS passages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL UNIQUE,          -- ISO, e.g. 2026-09-24
    text            TEXT NOT NULL,
    difficulty_note TEXT NOT NULL DEFAULT '',      -- "I found this difficult" box
    answered_on     TEXT                           -- date of first saved answer, NULL if untouched
);

CREATE TABLE IF NOT EXISTS questions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    passage_id     INTEGER NOT NULL REFERENCES passages(id) ON DELETE CASCADE,
    position       INTEGER NOT NULL,
    question       TEXT NOT NULL,
    correct_answer TEXT NOT NULL DEFAULT '',
    given_answer   TEXT NOT NULL DEFAULT '',
    UNIQUE (passage_id, position)
);

CREATE TABLE IF NOT EXISTS saved_words (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    word       TEXT NOT NULL UNIQUE,
    note       TEXT NOT NULL DEFAULT '',
    date_added TEXT NOT NULL,
    passage_id INTEGER REFERENCES passages(id) ON DELETE SET NULL
);
"""


@contextmanager
def connection():
    """One transaction per use: commits on success, rolls back on error."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db():
    with connection() as conn:
        conn.executescript(SCHEMA)


# ------------------------------------------------------------
# Dates
# ------------------------------------------------------------

def parse_date(text):
    """Accepts 2026-09-24, 24|09|2026, 24/09/2026 (day first), 24-09-2026, 24.09.2026."""
    text = str(text).strip()
    for fmt in ("%Y-%m-%d", "%d|%m|%Y", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError(f"can't read date {text!r}")


# ------------------------------------------------------------
# Reading
# ------------------------------------------------------------

def count_passages():
    with connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM passages").fetchone()[0]


def get_passage_for_date(date_iso):
    """Returns a dict with a 'questions' list, or None if that day has no passage."""
    with connection() as conn:
        row = conn.execute("SELECT * FROM passages WHERE date = ?", (date_iso,)).fetchone()
        if row is None:
            return None
        passage = dict(row)
        passage["questions"] = [
            dict(r) for r in conn.execute(
                "SELECT * FROM questions WHERE passage_id = ? ORDER BY position",
                (passage["id"],))
        ]
        return passage


# ------------------------------------------------------------
# Writing
# ------------------------------------------------------------

def _fit(items, n, label):
    """Pad or trim a list to n items. Refuses to drop anything non-empty."""
    items = [str(x) for x in items]
    extra = [x for x in items[n:] if x.strip()]
    if extra:
        raise ValueError(f"{len(extra)} extra non-empty {label} beyond the {n} questions")
    return (items + [""] * n)[:n]


def add_passage(date_text, text, questions, correct_answers,
                given_answers=None, answered_on=None, difficulty_note=""):
    iso = parse_date(date_text)
    n = len(questions)
    correct = _fit(correct_answers, n, "correct answers")
    given = _fit(given_answers or [], n, "given answers")
    with connection() as conn:
        if conn.execute("SELECT 1 FROM passages WHERE date = ?", (iso,)).fetchone():
            raise ValueError(f"a passage for {iso} already exists")
        cur = conn.execute(
            "INSERT INTO passages (date, text, difficulty_note, answered_on) VALUES (?, ?, ?, ?)",
            (iso, text, difficulty_note, answered_on))
        passage_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO questions (passage_id, position, question, correct_answer, given_answer) "
            "VALUES (?, ?, ?, ?, ?)",
            [(passage_id, i, questions[i], correct[i], given[i]) for i in range(n)])
    return passage_id


def save_answers(passage_id, text, difficulty_note, answers):
    """answers is a list of (question_id, answer_text). Safe to call as often as you like."""
    any_answer = any(a.strip() for _, a in answers)
    with connection() as conn:
        conn.execute(
            "UPDATE passages SET text = ?, difficulty_note = ?, "
            "answered_on = COALESCE(answered_on, ?) WHERE id = ?",
            (text, difficulty_note, date.today().isoformat() if any_answer else None, passage_id))
        conn.executemany(
            "UPDATE questions SET given_answer = ? WHERE id = ?",
            [(a, qid) for qid, a in answers])


def add_saved_word(word, note="", passage_id=None):
    """Returns True if added, False if the word was already saved."""
    with connection() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO saved_words (word, note, date_added, passage_id) VALUES (?, ?, ?, ?)",
            (word.strip(), note, date.today().isoformat(), passage_id))
        return cur.rowcount == 1

def get_oldest_unanswered_date(exclude=None):
    """Oldest passage dated today or earlier with no saved answers, skipping `exclude`."""
    with connection() as conn:
        row = conn.execute(
            "SELECT date FROM passages "
            "WHERE answered_on IS NULL AND date <= ? AND date <> ? "
            "ORDER BY date LIMIT 1",
            (date.today().isoformat(), exclude or "")).fetchone()
        return row["date"] if row else None

init_db()
