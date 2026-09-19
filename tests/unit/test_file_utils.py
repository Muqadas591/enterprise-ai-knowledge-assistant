from app.utils.file_utils import (
    get_file_extension,
    is_allowed_extension,
)


def test_get_file_extension() -> None:

    assert get_file_extension("report.PDF") == ".pdf"


def test_allowed_extension() -> None:

    allowed = [
        ".pdf",
        ".docx",
        ".txt",
    ]

    assert is_allowed_extension(
        "report.pdf",
        allowed,
    )

    assert not is_allowed_extension(
        "report.exe",
        allowed,
    )
