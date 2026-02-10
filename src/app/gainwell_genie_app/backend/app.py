from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .._metadata import app_name, dist_dir
from .config import AppConfig
from .router import api
from .runtime import Runtime
from .utils import add_not_found_handler
from .logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = AppConfig()
    logger.info("Starting app with configuration: %s", config)
    runtime = Runtime(config)
    app.state.config = config
    app.state.runtime = runtime
    yield


app = FastAPI(title=app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api)

if dist_dir.exists():
    ui = StaticFiles(directory=str(dist_dir), html=True)
    app.mount("/", ui)
else:
    logger.warning("UI dist_dir %s not found; run 'apx build' or 'apx frontend build' from app root", dist_dir)

add_not_found_handler(app)
