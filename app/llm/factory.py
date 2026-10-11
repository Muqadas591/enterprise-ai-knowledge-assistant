import logging
from collections.abc import AsyncIterator

from app.core.config import settings
from app.llm.base import LLMResponse, LLMService
from app.llm.providers.demo_provider import DemoLLMService
from app.llm.providers.gemini_provider import GeminiLLMService
from app.llm.providers.openai_provider import OpenAILLMService

logger = logging.getLogger(__name__)


class GeminiWithOpenAIFallback(LLMService):
    def __init__(self) -> None:
        self.primary = GeminiLLMService()
        self.fallback: OpenAILLMService | None = None

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMResponse:
        try:
            return self.primary.generate(system_prompt, user_prompt)
        except Exception:
            if not (settings.OPENAI_API_KEY or settings.LLM_API_KEY):
                raise

            logger.exception("Gemini generation failed; falling back to OpenAI")
            if self.fallback is None:
                self.fallback = OpenAILLMService()
            return self.fallback.generate(system_prompt, user_prompt)

    async def stream(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> AsyncIterator[str]:
        emitted = False
        try:
            async for token in self.primary.stream(
                prompt=user_prompt,
                system_instruction=system_prompt,
            ):
                emitted = True
                yield token
        except Exception:
            if emitted or not (settings.OPENAI_API_KEY or settings.LLM_API_KEY):
                raise

            logger.exception("Gemini streaming failed; falling back to OpenAI")
            if self.fallback is None:
                self.fallback = OpenAILLMService()
            response = self.fallback.generate(system_prompt, user_prompt)
            if response.content:
                yield response.content


def get_llm_service() -> LLMService:
    provider = settings.LLM_PROVIDER.lower()

    if provider == "gemini":
        if settings.GEMINI_API_KEY:
            return GeminiWithOpenAIFallback()
        if settings.OPENAI_API_KEY or settings.LLM_API_KEY:
            logger.warning("Gemini key is missing; using OpenAI as the configured fallback")
            return OpenAILLMService()
        raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini.")

    if provider == "openai":
        return OpenAILLMService()

    if provider in {"demo", "mock"}:
        return DemoLLMService()

    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
