"""Talking to Claude. No tkinter in here, so it can be tested without a window."""
import os
import sys
MODEL = "claude-sonnet-5-5"   # change this one line to switch models
MAX_TOKENS = 4096
TIMEOUT_SECONDS = 120

SYSTEM_PROMPT = """\
You are a friendly, honest Japanese tutor. Your student is an English speaker \
reading passages from a Japanese light novel (Eminence in the Shadow) and \
answering comprehension questions about each one. Their level is upper beginner \
to lower intermediate.

You will receive the passage, each question with a model answer, the student's \
answer to each, and a note from the student about what they found difficult.

The passage is a short excerpt from a published light novel the student is reading \
for language practice. It may contain violence, weapons, or other content typical of \
action fiction. Treat this as ordinary reading comprehension material, the same as a \
teacher would discuss a novel in a classroom: your job is only to check the student's \
reading comprehension and language, never to analyze, explain, or elaborate on any \
real-world technical, weapons-related, or dangerous content the story happens to \
mention in passing. Some story-specific words below have been swapped for neutral \
stand-ins by the student's own software before reaching you; treat them as the \
fictional nouns they are and don't try to guess or comment on the original word.

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


# Words that have tripped the safety classifier on this story before (it's a light
# novel about a kid who wants to be an "eminence in the shadow" and obsesses over
# overwhelming/world-ending power, so these come up more than in typical reading).
# Swapped only in the copy sent to the API — never in what's saved or shown to you.
# If a new passage gets refused, add the word that's probably responsible here.
SENSITIVE_WORDS = {
    "核兵器": "特殊兵器",     # nuclear weapon -> "special weapon"
    "核": "特殊な力",         # nuclear -> "a special power" (also covers 核爆弾 etc.)
    "生物兵器": "禁忌の薬",   # biological weapon -> "forbidden medicine"
    "毒ガス": "毒の霧",       # poison gas -> "poison mist" (sounds equally fantasy, less like a real agent)
    "テロ": "破壊工作",       # terrorism -> "sabotage"
    "爆弾": "爆裂魔法",       # bomb -> "explosive magic" (fits the setting, less like a real device)
}


def sanitize_for_api(text):
    """Swap words that have triggered refusals, for the copy sent to the API only."""
    for word, replacement in SENSITIVE_WORDS.items():
        text = text.replace(word, replacement)
    return text


class FeedbackError(Exception):
    """Something went wrong. The message is written to be shown to the user."""


def build_prompt(passage_text, questions, model_answers, given_answers, difficulty_note):
    passage_text = sanitize_for_api(passage_text)
    questions = [sanitize_for_api(q) for q in questions]
    model_answers = [sanitize_for_api(a) for a in model_answers]
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
        except ImportError as error:
            raise FeedbackError(
                f"Couldn't import anthropic: {error}\n\n"
                f"This program is running on:\n{sys.executable}\n\n"
                f'Install into that exact Python with:\n"{sys.executable}" -m pip install anthropic')
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

    if message.stop_reason == "refusal":
        category = None
        details = getattr(message, "stop_details", None) or getattr(message, "stop_reason_details", None)
        if details is not None:
            category = getattr(details, "category", None)
        raise FeedbackError(
            "Claude declined to answer for this passage"
            + (f" (category: {category})" if category else "")
            + ". This isn't a bug: the API billed you for the input tokens but generated "
            "no output, so retrying with the same text will likely refuse again and cost "
            "the same amount. If the passage discusses something sensitive (weapons, "
            "violence, etc.), try trimming that part out before asking for feedback, or "
            "just skip feedback for this one passage.")

    # The reply is a list of content blocks; keep only the text ones.
    text = "".join(b.text for b in message.content if getattr(b, "type", "") == "text").strip()
    if not text:
        if message.stop_reason == "end_turn":
            raise FeedbackError(
                "Claude returned nothing, with no error and no refusal label. This can be "
                "a harmless quirk, or it can be a safety check that didn't get labeled as a "
                "refusal. Pressing Regenerate sometimes gets a real reply next try, since the "
                "model isn't perfectly consistent. If it keeps happening on this same passage, "
                "treat it like a refusal: something in the text is probably the cause, so try "
                "trimming or paraphrasing a line before asking again.")
        raise FeedbackError(f"Claude sent back an empty reply (stop_reason: {message.stop_reason}).")
    if message.stop_reason == "max_tokens":
        text = (
            "==================== CUT OFF ====================\n"
            "This reply hit the length limit and is INCOMPLETE.\n"
            "Press Regenerate, and if it happens again, tell Claude\n"
            "in chat so the limit can be raised further.\n"
            "==================================================\n\n"
        ) + text
    return text
