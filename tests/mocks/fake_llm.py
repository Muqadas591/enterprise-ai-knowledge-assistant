from app.llm.base import LLMResponse, LLMService


class FakeLLMService(LLMService):
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMResponse:
        return LLMResponse(
            content="Test answer [S1]",
            model="fake-model",
        )
