from collections.abc import AsyncIterator

from google import genai
from google.genai import types

from app.core.config import settings
from app.llm.base import LLMResponse, LLMService

class GeminiLLMService(LLMService):
    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMResponse:
        config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=settings.LLM_MAX_OUTPUT_TOKENS,
            system_instruction=system_prompt,
        )
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=config,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        usage = None
        if response.usage_metadata:
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }
        
        return LLMResponse(
            content=response.text,
            model=self.model,
            usage=usage,
        )

    async def stream(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> AsyncIterator[str]:
        config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=settings.LLM_MAX_OUTPUT_TOKENS,
            system_instruction=system_instruction,
        )
        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt,
            config=config,
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text
         