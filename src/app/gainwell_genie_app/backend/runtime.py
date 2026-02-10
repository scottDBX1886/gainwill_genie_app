from databricks.sdk import WorkspaceClient

from .config import AppConfig


class Runtime:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    @property
    def ws(self) -> WorkspaceClient:
        return WorkspaceClient()
