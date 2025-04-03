import traceback
from typing import List

import httpx
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db
from app.logs.config_server_logs import server_logger
from app.authentication import api_token
import app.meteofrance.utils as utils
import app.meteofrance.service as meteofrance_service
from app.meteofrance.schemas import MeteoFranceInfrahoraireMessage

router = APIRouter()

@router.get("/receive_message/", dependencies=[Depends(api_token)])
async def receive_message(station_id: str, db: AsyncSession = Depends(get_db)):
    """
    Receive message from meteofrance
    :param station_id:
    :param db:
    :return:
    """
    async with httpx.AsyncClient() as client:
        external_api_uri = f"{settings.METEOFRANCE_URL}{settings.METEOFRANCE_OBS_INFRAHORAIRE}"
        params = {
            "id_station": station_id,
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

        response_data: List[MeteoFranceInfrahoraireMessage] = utils.consume_meteofrance_message(response.json())

        await meteofrance_service.process_meteofrance_infrahoraire(db, response_data)

        return [data.model_dump() for data in response_data]