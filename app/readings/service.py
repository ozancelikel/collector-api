import logging

from sqlalchemy.ext.asyncio import AsyncSession

import app.crud.barani_sensors as db_service
from app.models.models import BaraniHelixSensors, BaraniWindSensors
from app.readings.schemas import HelixMessage, WindMessage


async def process_helix_message(db: AsyncSession, message: HelixMessage):
    logging.info(f"HELIX -- Received message: {message}")

    resp: BaraniHelixSensors = await db_service.create_barani_helix_reading(db, message)

    response = {"status": "success", "message": "helix reading created.", "details": f"{resp.__dict__}"}

    logging.info(response)

    return response


async def process_wind_message(db: AsyncSession, message: WindMessage):
    logging.info(f"WIND -- Received message: {message}")

    resp: BaraniWindSensors = await db_service.insert_barani_wind_reading(db, message)

    response = {"status": "success", "message": "wind reading created.", "details": f"{resp.__dict__}"}

    logging.info(response)

    return response


async def process_get_sensor_by_serial_number(db: AsyncSession, sn: str):
    logging.info(f"HELIX -- GET Received, serial number: {sn}")

    resp = await db_service.get_sensor_by_serial_number(db, sn)

    response = {"status": "success", "message": "Sensor readings returned.", "details": f"{resp.__dict__}"}

    logging.info(response)

    return response
