from fastapi import Request, HTTPException

from app.config import settings


def api_token(request: Request):
    token = request.headers.get("api-key")
    if token != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Token unauthorized.")
    return token