from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    token: str


class FileConfig(BaseSettings):
    user_data: Path
    cats_path: Path


class Settings(BaseSettings):
    bot_config: BotConfig
    file_config: FileConfig

    model_config = SettingsConfigDict(
        env_file=(
            ".env.template",
            ".env",
        ),
        env_nested_delimiter="__",
    )


settings = Settings()

if __name__ == "__main__":
    print(settings.bot_config.token)
