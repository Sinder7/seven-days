from pydantic_settings import BaseSettings


class Config(BaseSettings):
    db_url: str = f"sqlite:aiosqlte:///db.sqlite3"
    db_echo: bool = True


config: Config = Config()