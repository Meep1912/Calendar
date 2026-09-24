from tkinter import *
from tkinter import ttk
from datetime import date, datetime

import comprehension_db as db

FONT = ("Yu Gothic UI", 12)
FONT_BOLD = ("Yu Gothic UI", 12, "bold")

PAD = 10
PASSAGE_TOP, PASSAGE_HEIGHT = 45, 320
QUESTIONS_TOP = 385
QUESTION_HEIGHT, ANSWER_HEIGHT, ROW_HEIGHT = 56, 56, 130
NOTE_HEIGHT = 100
AUTOSAVE_MS = 3 * 60 * 1000


# ------------------------------------------------------------
# Generic helpers
# ------------------------------------------------------------

def make_scrollable_frame(parent, width=800, height=1000):
    """Returns a frame inside a scrollable canvas. The frame always matches the canvas width."""
    canvas = Canvas(parent, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    frame = Frame(canvas, width=width, height=height)

    window_id = canvas.create_window((0, 0), window=frame, anchor="nw")
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    parent.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))  # Windows
    parent.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))                     # Linux
    parent.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
    return frame


def make_text_box(parent, y, height, text="", read_only=False):
    """A word-wrapping, undo-able text box that stretches with the window."""
    box = Text(parent, font=FONT, wrap="word", undo=True, maxundo=-1)
    box.place(x=PAD, y=y, relwidth=1, width=-2 * PAD, height=height)
    box.insert("1.0", text)
    if read_only:
        box.config(state="disabled")
        box.bind("<Button-1>", lambda e: box.focus_set())   # so you can still select and copy
    return box


def start_autosave(window, save, every_ms=AUTOSAVE_MS):
    def tick():
        if not window.winfo_exists() or not save():
            return          # window closed, or its widgets were replaced
        window.after(every_ms, tick)
    window.after(every_ms, tick)


# ------------------------------------------------------------
# The comprehension screen
# ------------------------------------------------------------

def build_question_rows(frame, questions):
    """Returns a list of (question_id, answer_box)."""
    rows = []
    for i, q in enumerate(questions):
        y = QUESTIONS_TOP + i * ROW_HEIGHT
        make_text_box(frame, y, QUESTION_HEIGHT, q["question"], read_only=True)
        answer = make_text_box(frame, y + QUESTION_HEIGHT + 6, ANSWER_HEIGHT, q["given_answer"])
        rows.append((q["id"], answer))
    return rows


def build_difficulty_box(frame, note, y):
    Label(frame, text="What did you find difficult?", font=FONT).place(x=PAD, y=y)
    return make_text_box(frame, y + 30, NOTE_HEIGHT, note)

def draw_comprehension(day, month, year, parent):
    the_date = date(year, month, day).isoformat()
    passage = db.get_passage_for_date(the_date)

    n = len(passage["questions"]) if passage else 0
    note_y = QUESTIONS_TOP + n * ROW_HEIGHT
    frame = make_scrollable_frame(parent, height=note_y + 30 + NOTE_HEIGHT + 40)

    Label(frame, text=the_date, font=FONT_BOLD).place(x=PAD, y=8)
    Button(frame, text="Add", command=add_question_view).place(x=130, y=5)
    status = Label(frame, text="")
    status.place(x=370, y=8)

    passage_box = note_box = rows = None   # filled in below when there is a passage

    def save():
        if passage is None:
            return True
        try:
            db.save_answers(
                passage["id"],
                passage_box.get("1.0", "end-1c"),
                note_box.get("1.0", "end-1c"),
                [(qid, box.get("1.0", "end-1c")) for qid, box in rows])
            status.config(text="Saved " + datetime.now().strftime("%H:%M:%S"))
            return True
        except TclError:
            return False    # widgets are gone

    def jump_to_unfinished():
        target = db.get_oldest_unanswered_date(exclude=the_date)
        if target is None:
            status.config(text="Nothing unfinished")
            return
        save()
        for w in parent.winfo_children():
            w.destroy()
        y, m, d = map(int, target.split("-"))
        draw_comprehension(d, m, y, parent)

    def on_close():
        save()
        parent.destroy()

    Button(frame, text="Next unfinished", command=jump_to_unfinished).place(x=250, y=5)
    parent.protocol("WM_DELETE_WINDOW", on_close)
    start_autosave(parent, save)

    if passage is None:
        Label(frame, text="No passage for this day yet.", font=FONT).place(x=PAD, y=50)
        return

    passage_box = make_text_box(frame, PASSAGE_TOP, PASSAGE_HEIGHT, passage["text"])
    rows = build_question_rows(frame, passage["questions"])
    note_box = build_difficulty_box(frame, passage["difficulty_note"], note_y)
    Button(frame, text="Done!", command=save).place(x=190, y=5)

# ------------------------------------------------------------
# Adding new passages
# ------------------------------------------------------------

add_questions_frame = None


def add_question_view():
    global add_questions_frame
    if add_questions_frame is not None:
        add_questions_frame.destroy()

    add_questions_frame = Toplevel()
    add_questions_frame.title("Add comprehension")
    add_questions_frame.geometry("700x700")

    box = Text(add_questions_frame, font=FONT, wrap="word", undo=True, maxundo=-1)
    box.place(x=PAD, y=40, relwidth=1, relheight=1, width=-2 * PAD, height=-50)

    status = Label(add_questions_frame, text="", justify="left", wraplength=550)
    status.place(x=80, y=6)

    def on_done():
        added, problems = decode_question_data(box.get("1.0", "end-1c"))
        message = f"Added {added}."
        if problems:
            message += " Problems: " + "; ".join(problems)
        status.config(text=message)

    Button(add_questions_frame, text="Done!", command=on_done).place(x=10, y=5)


def _find_line(block, word):
    for i, line in enumerate(block):
        if line.strip() == word:
            return i
    raise ValueError(f"missing a '{word}' line")


def decode_question_data(data):
    """Parses pasted text (Date / Text / Questions / Answers blocks). Returns (added, problems)."""
    lines = [line.rstrip() for line in data.splitlines()]
    starts = [i for i, line in enumerate(lines) if line.strip() == "Date"]
    added, problems = 0, []

    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        block = lines[start:end]
        try:
            t = _find_line(block, "Text")
            q = _find_line(block, "Questions")
            a = _find_line(block, "Answers")
            date_text = block[1]
            text = "\n".join(block[t + 1:q]).strip()
            questions = [line for line in block[q + 1:a] if line.strip()]
            answers = [line for line in block[a + 1:] if line.strip()]
            db.add_passage(date_text, text, questions, answers)
            added += 1
        except (ValueError, IndexError) as e:
            problems.append(f"entry {n + 1}: {e}")

    return added, problems
