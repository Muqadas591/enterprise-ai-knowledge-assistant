from app.llm.base import LLMService

QUERY_REWRITE_PROMPT = """
You rewrite user questions for enterprise document retrieval.

Given the conversation history and the latest user question,
produce a standalone search query.

Rules:

1. Preserve the user's intent.
2. Resolve references such as:
   - it
   - they
   - this
   - that
   - the above
   - previous policy
3. Do not answer the question.
4. Do not add facts.
5. Return only the rewritten search query.
6. If the question is already standalone, return it unchanged.
"""


class QueryRewriteService:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def rewrite(self, question: str, history: str) -> str:
        prompt = f"""
Conversation history:

{history}

Latest user question:

{question}

Rewrite the latest question as a standalone
enterprise document search query.
"""
        response = self.llm.generate(
            system_prompt=QUERY_REWRITE_PROMPT,
            user_prompt=prompt,
        )
        rewritten = response.content.strip()
        return rewritten or question
