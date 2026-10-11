from app.rag.prompts.rag_prompt import (
    RAG_SYSTEM_PROMPT,
    build_rag_user_prompt,
)


def test_prompt_contains_question():
    prompt = build_rag_user_prompt("What is the leave policy?", "context")

    assert "What is the leave policy?" in prompt


def test_prompt_contains_context():
    prompt = build_rag_user_prompt("question", "annual leave context")

    assert "annual leave context" in prompt
    assert "ONLY" in RAG_SYSTEM_PROMPT
