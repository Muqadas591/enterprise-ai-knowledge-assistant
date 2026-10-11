from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    temperature: float = 0.0
    max_tokens: int = 1000
    api_key: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


llm_settings = LLMSettings()
