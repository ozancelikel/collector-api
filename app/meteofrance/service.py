from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.meteofrance_sensors import create_meteofrance_sensor
from app.meteofrance.schemas import MeteoFranceInfrahoraireMessage


async def process_meteofrance_infrahoraire(db: AsyncSession,
                                           message: List[MeteoFranceInfrahoraireMessage]):
    """
    Process "infrahoraire-6m" messages from MeteoFrance.
    These messages contain information for the last reading of the sensor.

    :param db:
    :param message:
    :return:
    """
    resp = await create_meteofrance_sensor(db, message)
    print(resp)
    pass
