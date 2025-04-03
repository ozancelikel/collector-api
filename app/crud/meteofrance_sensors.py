from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.meteofrance.schemas import MeteoFranceInfrahoraireMessage
from app.models.models import MeteoFranceData
from app.logs.config_server_logs import server_logger as logger

async def create_meteofrance_sensor(db: AsyncSession, message: List[MeteoFranceInfrahoraireMessage]):
    for data in message:
        meteo_france_data: MeteoFranceData = MeteoFranceData.from_dict(data.model_dump())
        db.add(meteo_france_data)
    try:
        await db.commit()
        await db.refresh(meteo_france_data)
    except Exception as e:
        logger.error(e)
        raise e
    return {"message": "Weather data uploaded successfully", "geo_id_insee": meteo_france_data.geo_id_insee}