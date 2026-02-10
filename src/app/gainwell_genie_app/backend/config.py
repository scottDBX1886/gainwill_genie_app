from pathlib import Path
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .._metadata import app_name, app_slug

# Project root = directory containing pyproject.toml (parent of gainwell_genie_app)
project_root = Path(__file__).resolve().parent.parent.parent
env_file = project_root / ".env"

try:
    from dotenv import load_dotenv
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
except ImportError:
    pass


class AppConfig(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=env_file, env_prefix=f"{app_slug.upper()}_", extra="ignore"
    )
    app_name: str = Field(default=app_name)

    @property
    def static_assets_path(self) -> Path:
        from importlib import resources
        return Path(str(resources.files(app_slug))).joinpath("__dist__")
