from fastapi import FastAPI

from .routes.table_converter import router as table_converter_router

__all__ = ("app",)

app = FastAPI()

app.include_router(table_converter_router)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {
        "info": "Healthy",
    }
