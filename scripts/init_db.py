from alembic import command
from alembic.config import Config


def init_database() -> None:
    alembic_config = Config("alembic.ini")

    command.upgrade(
        alembic_config,
        "head",
    )

    print("Database migrations applied successfully.")


if __name__ == "__main__":
    init_database()
