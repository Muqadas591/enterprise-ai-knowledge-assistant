import hashlib
from pathlib import Path
from uuid import uuid4


def calculate_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def generate_stored_filename(
    original_filename: str,
) -> str:
    extension = get_file_extension(original_filename)

    return f"{uuid4().hex}{extension}"


def is_allowed_extension(
    filename: str,
    allowed_extensions: list[str],
) -> bool:
    extension = get_file_extension(filename)

    return extension in allowed_extensions
