from openai import OpenAI

from app.core.config import settings
from app.llm.base import LLMResponse, LLMService


class OpenAILLMService(LLMService):
    def __init__(self) -> None:
        api_key = settings.OPENAI_API_KEY or settings.LLM_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY (or legacy LLM_API_KEY) is not configured.")

        self.client = OpenAI(api_key=api_key)
        self.model = settings.OPENAI_MODEL or settings.LLM_MODEL

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMResponse:
        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
            temperature=settings.LLM_TEMPERATURE,
            max_output_tokens=settings.LLM_MAX_TOKENS,
        )

        return LLMResponse(
            content=response.output_text,
            model=self.model,
            usage=None,
        )
