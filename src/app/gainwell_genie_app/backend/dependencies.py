from typing import Annotated

from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
from fastapi import Depends, Header, Request

from .config import AppConfig
from .runtime import Runtime


def get_config(request: Request) -> AppConfig:
    if not hasattr(request.app.state, "config"):
        raise RuntimeError(
            "AppConfig not initialized. "
            "Ensure app.state.config is set during application lifespan startup."
        )
    return request.app.state.config


ConfigDep = Annotated[AppConfig, Depends(get_config)]


def get_runtime(request: Request) -> Runtime:
    if not hasattr(request.app.state, "runtime"):
        raise RuntimeError(
            "Runtime not initialized. "
            "Ensure app.state.runtime is set during application lifespan startup."
        )
    return request.app.state.runtime


RuntimeDep = Annotated[Runtime, Depends(get_runtime)]


def get_obo_ws(
    token: Annotated[str | None, Header(alias="X-Forwarded-Access-Token")] = None,
) -> WorkspaceClient:
    if not token:
        raise ValueError(
            "User token is required. When running in Databricks Apps, enable user authorization "
            "and add scopes 'dashboards.genie' and 'sql' so the app can call Genie on your behalf."
        )
    cfg = Config()
    return WorkspaceClient(host=cfg.host, token=token, auth_type="pat")
