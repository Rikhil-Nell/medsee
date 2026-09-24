"""OpenAI model construction for Pydantic AI agents."""

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from medsee.core.config import Settings


def create_openai_chat_model(settings: Settings) -> OpenAIChatModel:
    """Build an OpenAI chat model with explicit provider credentials from settings."""
    provider = OpenAIProvider(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
    return OpenAIChatModel(settings.openai_model, provider=provider)
