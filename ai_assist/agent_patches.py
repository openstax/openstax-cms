"""Runtime overrides for wagtail-ai's bundled agents."""


def route_content_feedback_provider():
    """Point the content-feedback agent at the OpenAI ``content_feedback`` provider.

    Content feedback is the only wagtail-ai agent that requests structured output
    (``response_format``). any-llm 0.20.3's Anthropic provider raises
    ``UnsupportedParameterError`` on that parameter, so on our Anthropic
    ``default`` provider the feature always errors ("Unable to get page content
    for analysis"). OpenAI's provider supports ``response_format``.

    ``ContentFeedbackAgent`` hardcodes ``provider_alias = "default"`` and exposes
    no setting to override it (unlike image description's
    ``IMAGE_DESCRIPTION_PROVIDER``), so we set the class attribute here. Idempotent.
    Remove once any-llm is upgraded to >=1.x, whose Anthropic provider supports
    structured output — then content feedback can return to Claude.
    """
    from wagtail_ai.agents.content_feedback import ContentFeedbackAgent

    ContentFeedbackAgent.provider_alias = "content_feedback"
