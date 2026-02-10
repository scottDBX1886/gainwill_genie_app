from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .._metadata import api_prefix, dist_dir
from .logger import logger


def add_not_found_handler(app: FastAPI):
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.info(
            "HTTP exception handler called for request %s with status code %s",
            request.url.path,
            exc.status_code,
        )
        if exc.status_code == 404:
            path = request.url.path
            accept = request.headers.get("accept", "")
            is_api = path.startswith(api_prefix)
            is_get_page_nav = request.method == "GET" and "text/html" in accept
            looks_like_asset = "." in path.split("/")[-1]
            index_html = dist_dir / "index.html"
            if (not is_api) and is_get_page_nav and (not looks_like_asset) and index_html.exists():
                return FileResponse(index_html)
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    app.exception_handler(StarletteHTTPException)(http_exception_handler)
