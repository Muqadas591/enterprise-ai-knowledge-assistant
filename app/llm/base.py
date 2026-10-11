from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict | None = None


class LLMService(ABC):
    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMResponse:
        """Generate a response using the app's synchronous RAG contract."""
        raise NotImplementedError


class BaseLLM(ABC):

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> str:
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> AsyncIterator[str]:
        pass