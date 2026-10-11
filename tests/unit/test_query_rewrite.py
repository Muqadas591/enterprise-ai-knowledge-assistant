from app.llm.base import LLMResponse
from app.services.query_rewrite_service import QueryRewriteService


class StubLLM:
    def __init__(self, content: str):
        self.content = content
        self.calls: list[tuple[str, str]] = []

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        self.calls.append((system_prompt, user_prompt))
        return LLMResponse(content=self.content, model="stub-model")


def test_standalone_question_is_returned_from_llm():
    llm = StubLLM("What is the annual leave policy?")

    result = QueryRewriteService(llm).rewrite(
        "What is the annual leave policy?",
        "",
    )

    assert result == "What is the annual leave policy?"
    assert llm.calls


def test_ambiguous_question_is_rewritten_with_history():
    llm = StubLLM("What is the annual leave policy for probationary employees?")

    result = QueryRewriteService(llm).rewrite(
        "What about probationary employees?",
        "USER: What is the annual leave policy?\nASSISTANT: Employees receive 20 days.",
    )

    assert result == "What is the annual leave policy for probationary employees?"
    assert "What is the annual leave policy?" in llm.calls[0][1]
    assert "What about probationary employees?" in llm.calls[0][1]
