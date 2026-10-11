from app.core.security.hashing import hash_password, verify_password
from app.core.security.jwt import create_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register(
        self,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> User:
        if self.user_repository.get_by_email(email):
            raise ValueError("A user with this email already exists.")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role="user",
        )
        return self.user_repository.create(user)

    def authenticate(self, email: str, password: str) -> str:
        user = self.user_repository.get_by_email(email)
        if (
            not user
            or not user.is_active
            or not verify_password(
                password,
                user.hashed_password,
            )
        ):
            raise ValueError("Invalid email or password.")

        return create_access_token(subject=str(user.id))
