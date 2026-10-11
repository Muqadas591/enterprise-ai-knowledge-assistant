import pytest

from app.core.config import settings
from app.llm.base import LLMResponse, LLMService
from app.llm.providers.openai_provider import OpenAILLMService
from app.rag.prompts import RAG_SYSTEM_PROMPT, build_rag_user_prompt


def test_llm_response_contract():
    response = LLMResponse(content="answer", model="test-model")

    assert response.content == "answer"
    assert response.model == "test-model"


def test_llm_service_is_abstract():
    with pytest.raises(TypeError):
        LLMService()


def test_grounding_prompt_contains_context_and_question():
    prompt = build_rag_user_prompt("What is the policy?", "[S1] Policy content")

    assert "What is the policy?" in prompt
    assert "[S1] Policy content" in prompt
    assert "ONLY" in RAG_SYSTEM_PROMPT


def test_openai_provider_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", None)

    with pytest.raises(ValueError, match="LLM_API_KEY"):
        OpenAILLMService()
