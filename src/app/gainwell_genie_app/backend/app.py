from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
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

# Serve UI: explicit root so "/" always returns HTML; then mount static assets
_index_html = dist_dir / "index.html"
if _index_html.exists():
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def serve_root():
        return FileResponse(_index_html, media_type="text/html")

    ui = StaticFiles(directory=str(dist_dir), html=True)
    app.mount("/", ui)
else:
    logger.warning("UI dist_dir %s not found; run 'apx build' before deploy", dist_dir)

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def serve_root_fallback():
        return HTMLResponse(
            "<!DOCTYPE html><html><head><title>App</title></head><body>"
            "<h1>UI not built</h1><p>Run <code>apx build</code> in <code>src/app</code> then redeploy.</p>"
            "</body></html>",
            status_code=503,
        )

add_not_found_handler(app)
