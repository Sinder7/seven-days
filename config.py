from pydantic_settings import BaseSettings


class Config(BaseSettings):
    db_url: str = f"sqlite+aiosqlite:///./seven.db"
    db_echo: bool = True


config: Config = Config()
