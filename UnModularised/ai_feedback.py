"""Talking to Claude. No tkinter in here, so it can be tested without a window."""
import os

MODEL = "claude-sonnet-5"     # change this one line to switch models
MAX_TOKENS = 3000
TIMEOUT_SECONDS = 60

SYSTEM_PROMPT = """\
You are a friendly, honest Japanese tutor. Your student is an English speaker \
reading passages from a Japanese light novel (Eminence in the Shadow) and \
answering comprehension questions about each one. Their level is upper beginner \
to lower intermediate.

You will receive the passage, each question with a model answer, the student's \
answer to each, and a note from the student about what they found difficult.

How to read the input:
- The passage may contain English lines the student typed. Each is their own \
attempted translation of the Japanese line above it. Check them for accuracy.
- A model answer is one acceptable answer, not the only one. Judge whether the \
student's answer shows they understood the passage, not whether it matches word \
for word.
- If a model answer starts with (自由回答), the question is open-ended and has no \
right or wrong content. Comment only on the language.
- The student may answer in English, in Japanese, or by copying a line from the \
passage. Copying a line shows they found the right place, so say that, and \
encourage a rewrite in their own words next time.

How to reply: plain text only. Your reply is shown in a widget that does not \
render Markdown, so do not use asterisks, pound signs or tables. Use these \
headings, and skip any that don't apply:

Comprehension: one line per question: correct, partly correct, or off, with one \
short reason.
Translation notes: mistakes or missed nuance in their English lines. Point out \
dropped subjects and pronouns when they caused an error.
Japanese corrections: for any Japanese the student wrote, give a corrected \
version and say briefly what changed and why.
Worth remembering: at most three words or grammar points from the passage, \
chosen to address what they said they found difficult.

Be encouraging but specific, and don't flatter. If you are unsure about a \
nuance, say so instead of guessing. Do not invent details about the story \
beyond the passage. Keep the whole reply under about 350 words.
"""


class FeedbackError(Exception):
    """Something went wrong. The message is written to be shown to the user."""


def build_prompt(passage_text, questions, model_answers, given_answers, difficulty_note):
    parts = ["<passage>", passage_text.strip(), "</passage>", ""]
    for i, (q, model, given) in enumerate(zip(questions, model_answers, given_answers), 1):
        parts += [
            f"Question {i}: {q}",
            f"Model answer: {model}",
            f"Student's answer: {given.strip() or '(left blank)'}",
            "",
        ]
    parts += [
        "What the student found difficult:",
        difficulty_note.strip() or "(nothing written)",
    ]
    return "\n".join(parts)


def _explain(error):
    """Turn an SDK exception into a sentence a person can act on."""
    name = type(error).__name__
    if name == "AuthenticationError":
        return "The API key was rejected. Check that ANTHROPIC_API_KEY is correct."
    if name == "RateLimitError":
        return "Too many requests right now. Wait a minute and try again."
    if name in ("APIConnectionError", "APITimeoutError"):
        return "Couldn't reach the API. Are you online?"
    return f"The API call failed ({name}): {error}"


def ask_claude(prompt, client=None):
    """Send one prompt, return the reply text. Raises FeedbackError with a readable message.

    `client` exists so tests can pass a fake one instead of spending real money.
    """
    if client is None:
        try:
            import anthropic
        except ImportError:
            raise FeedbackError("The anthropic library isn't installed. Run: pip install anthropic")
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise FeedbackError(
                "ANTHROPIC_API_KEY isn't set. Create a key in the Anthropic Console, then "
                'run setx ANTHROPIC_API_KEY "your-key" and reopen your terminal.')
        client = anthropic.Anthropic(timeout=TIMEOUT_SECONDS)

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as error:
        raise FeedbackError(_explain(error)) from error

    # The reply is a list of content blocks; keep only the text ones.
    text = "".join(b.text for b in message.content if getattr(b, "type", "") == "text").strip()
    if not text:
        raise FeedbackError("Claude sent back an empty reply. Try again.")
    if message.stop_reason == "max_tokens":
        text += "\n\n(The reply was cut off because it hit the length limit.)"
    return text
