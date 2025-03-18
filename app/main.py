import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.barani.router import router as barani_router
from app.campbell.router import router as campbell_router
from app.davis.router import router as davis_router
from app.tasks.scheduler import start_scheduler, shutdown_scheduler
from app.logs.config_server_logs import server_logger


class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        server_logger.info(f"Incoming request body: {body.decode()}")

        response = await call_next(request)
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to start the scheduler."""
    start_scheduler()
    yield  # Keep FastAPI running
    shutdown_scheduler()

app = FastAPI(lifespan=lifespan)

app.add_middleware(LogRequestMiddleware)

app.include_router(barani_router, prefix="/messages")
app.include_router(campbell_router)
app.include_router(davis_router, prefix="/davis")

@app.get("/")
def health_check():
    return {"status": "running"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = exc.errors()
    server_logger.error(f"Validation error on {request.url}: {error_details}")
    return JSONResponse(
        status_code=422,
        content={
            "status": 422,
            "error": "Validation Failed",
            "details": error_details
        },
    )