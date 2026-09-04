"""OpenStax brand-tuned starter prompts for wagtail-ai.

Voice: mission-driven, warm, plain language, accessible. No hype. Output should
read so a faculty member or student could follow it.
"""

# `method` values are Prompt.Method enum member NAMES (REPLACE / APPEND); the
# seeding command maps them to the stored lowercase values.
OPENSTAX_PROMPTS = [
    {
        "label": "Improve writing (OpenStax voice)",
        "description": "Rewrite in OpenStax's clear, accessible, mission-driven voice.",
        "prompt": (
            "Rewrite the following text in OpenStax's voice: warm, mission-driven, "
            "and accessible. Use plain language a faculty member or student could "
            "easily follow. Avoid hype, jargon, and marketing buzzwords. Keep the "
            "original meaning and any factual claims unchanged. Return only the "
            "rewritten text."
        ),
        "method": "REPLACE",
    },
    {
        "label": "Generate alt text",
        "description": "Factual, accessible alt text for an image.",
        "prompt": (
            "Write concise, factual alt text describing this image for screen-reader "
            "users. Maximum 125 characters. Do not begin with 'image of' or "
            "'picture of'. Describe what is shown, not its styling. Return only the "
            "alt text."
        ),
        "method": "REPLACE",
    },
    {
        "label": "Meta description",
        "description": "Concise, accessible search/meta description of a page.",
        "prompt": (
            "Summarize the following page content as a meta description for search "
            "results. One or two plain-language sentences, under 160 characters, "
            "accurate and free of hype. Return only the description."
        ),
        "method": "REPLACE",
    },
]


# Exemplars, not retrieval: the vector index embeds titles and meta descriptions
# only, and retrieving from our own body copy would teach the model the voice we
# are trying to move away from.
VOICE_EXEMPLARS = [
    (
        "OpenStax leverages cutting-edge technology to deliver best-in-class "
        "learning solutions that empower educators to drive student outcomes.",
        "OpenStax builds free textbooks and learning tools that teachers can use "
        "the day they find them.",
    ),
    (
        "Our revolutionary platform has disrupted the textbook industry, saving "
        "students an unprecedented $2 billion and counting!",
        "Students have saved more than $2 billion using OpenStax books instead of "
        "buying commercial textbooks.",
    ),
    (
        "Faculty may utilize the aforementioned ancillary resources subsequent to "
        "verification of their instructor status.",
        "Once we confirm you teach the course, you can download the instructor "
        "resources.",
    ),
]

VOICE_RULES = """You are rewriting copy for openstax.org.

OpenStax is a nonprofit educational initiative at Rice University. We publish
free, openly licensed textbooks and learning tools, and we sell a few paid
platforms such as OpenStax Assignable.

Voice:
- Mission-driven, accessible, warm.
- Plain language over jargon. If a faculty member or student could not follow
  it, it is wrong.
- Confident about our impact without bragging. No hype, no over-promising, no
  exclamation marks.
- Say what something is and what the reader can do with it.

House terms: an "adoption" is an instructor formally using an OpenStax book in a
course; supporters and donors are "Mission Makers"; our two markets are HE and
K12; "faculty" and "instructors" are interchangeable, and K12 uses "teacher"."""


def voice_prompt(brief, allowed_tags):
    """Build the instruction sent alongside the HTML fragment being rewritten."""
    examples = "\n\n".join(
        f"Before: {before}\nAfter: {after}" for before, after in VOICE_EXEMPLARS
    )
    return f"""{VOICE_RULES}

Examples of the rewrite:

{examples}

{brief}

Rewrite the HTML fragment the user sends you.

Rules for your reply:
- Return HTML only. No markdown, no code fences, no commentary.
- Keep every factual claim, name, number, and link target unchanged.
- Keep the existing markup: same links, same emphasis, same headings, same
  number of blocks, in the same order.
- Use only these tags: {allowed_tags}.
- Keep the length within about a quarter of the original."""
