import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.readings.router import router as barani_router

logging.basicConfig(
    filename="server.log",  # Shared log file
    level=logging.INFO,  # Default level (services can override)
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        logger.info(f"Incoming request body: {body.decode()}")

        response = await call_next(request)
        return response


app = FastAPI()

app.add_middleware(LogRequestMiddleware)

app.include_router(barani_router, prefix="/messages")


@app.get("/")
def health_check():
    return {"status": "running"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = exc.errors()
    logger.error(f"Validation error on {request.url}: {error_details}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Failed",
            "details": error_details
        },
    )
