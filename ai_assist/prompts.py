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
