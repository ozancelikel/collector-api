import traceback

import httpx
from fastapi import APIRouter, HTTPException, Depends

from app.config import settings
from app.davis.router import api_token
from app.logs.config_server_logs import server_logger
from app.authentication import api_token

router = APIRouter()

@router.get("/receive_message/", dependencies=[Depends(api_token)])
async def receive_message(station_id: str):
    id_station = "20004002" # must be a string babushka
    async with httpx.AsyncClient() as client:
        external_api_uri = f"{settings.METEOFRANCE_URL}{settings.METEOFRANCE_OBS_INFRAHORAIRE}"
        params = {
            "id_station": id_station,
            "format": settings.METEOFRANCE_OPTJSON,
        }
        headers = {"apikey": settings.METEOFRANCE_API_KEY}
        try:
            response = await client.get(external_api_uri, headers=headers, params=params)
        except Exception as e:
            server_logger.error(f"METEO-FR -- ERROR CODE 500 - Error parsing meteofrance response: {str(e)}")
            server_logger.error("".join(traceback.format_exception(None, e, e.__traceback__)))
            server_logger.error(f"Error during MeteoFrance API call: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        if response.status_code != 200:
            error = f"METEO-FR -- ERROR CODE 500 - Failed to fetch data from the meteofrance API. Error: {response.text}"
            server_logger.error(error)
            raise HTTPException(status_code=response.status_code, detail=error)

        response_data = response.json()

        return response_data