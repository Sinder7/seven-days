from pathlib import Path

from pydantic_settings import BaseSettings


class Config(BaseSettings):

    # daabase
    DATABASE_URL: str = f"sqlite+aiosqlite:///./seven.db"
    DATABASE_ECHO: bool = False

    # path dir
    PROJECT_ROOT: Path = Path(__file__).parent
    TEMPLATES_DIR: Path = PROJECT_ROOT / "src" / "templates"
    STATIC_DIR: Path = PROJECT_ROOT / "src" / "static"


config: Config = Config()
