import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExtractedPage:
    page_number: int | None
    text: str


@dataclass
class ExtractedDocument:
    pages: list[ExtractedPage]
    metadata: dict


class DocumentLoader(ABC):
    @abstractmethod
    def load(self, file_path: Path) -> ExtractedDocument:
        raise NotImplementedError


def normalize_whitespace(text: str) -> str:
    text = text.replace("\x00", " ")

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def clean_text(text: str) -> str:
    text = normalize_whitespace(text)

    return text
