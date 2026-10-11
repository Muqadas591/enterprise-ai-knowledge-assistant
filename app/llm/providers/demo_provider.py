from app.llm.base import LLMResponse, LLMService


class DemoLLMService(LLMService):
    """Deterministic local provider for development without API credits."""

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        if "Rewrite the latest question" in user_prompt:
            question = user_prompt.split("Latest user question:", 1)[-1]
            question = question.split("Rewrite the latest question", 1)[0].strip()
            history = user_prompt.split("Conversation history:", 1)[-1]
            if "probationary" in question.lower() and "annual leave" in history.lower():
                question = "What is the annual leave policy for probationary employees?"
            return LLMResponse(content=question, model="demo-model")

        return LLMResponse(
            content=(
                "Demo mode is active. Add OpenAI credits and set LLM_PROVIDER=openai "
                "for generated answers."
            ),
            model="demo-model",
        )
