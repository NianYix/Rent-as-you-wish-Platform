from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import admin_router, router
from app.core.config import get_settings
from app.core.exceptions import AppError, app_error_handler, http_error_handler

settings = get_settings()

app = FastAPI(title="Rent As You Wish API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_local else settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)

app.include_router(router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")

settings.upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.app_env}
