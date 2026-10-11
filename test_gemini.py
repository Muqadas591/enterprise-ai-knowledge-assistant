from app.llm.providers.gemini_provider import GeminiLLMService


def main() -> None:
    llm = GeminiLLMService()
    answer = llm.generate(
        system_prompt="Answer concisely and accurately.",
        user_prompt="Explain Retrieval-Augmented Generation in three sentences.",
    )
    print("\n--- GEMINI RESPONSE ---\n")
    print(answer.content)


if __name__ == "__main__":
    main()