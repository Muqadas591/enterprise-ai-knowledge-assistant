import re


class ConversationTitleService:
    MAX_TITLE_LENGTH = 60

    STOP_WORDS = {
        "what",
        "what's",
        "what is",
        "how",
        "how many",
        "how much",
        "can",
        "could",
        "would",
        "please",
        "tell",
        "me",
        "the",
        "a",
        "an",
        "is",
        "are",
        "do",
        "does",
        "about",
    }

    @classmethod
    def generate_title(cls, question: str) -> str:
        question = question.strip()

        if not question:
            return "New Conversation"

        # Remove punctuation
        cleaned = re.sub(
            r"[^\w\s-]",
            "",
            question,
        )

        words = cleaned.split()

        meaningful_words = [
            word
            for word in words
            if word.lower() not in cls.STOP_WORDS
        ]

        if not meaningful_words:
            meaningful_words = words

        title = " ".join(
            meaningful_words[:8]
        )

        title = title.strip().capitalize()

        if len(title) > cls.MAX_TITLE_LENGTH:
            title = (
                title[: cls.MAX_TITLE_LENGTH]
                .rsplit(" ", 1)[0]
                + "..."
            )

        return title or "New Conversation"