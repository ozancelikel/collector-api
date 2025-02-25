from sqlalchemy.ext.asyncio import AsyncSession

import app.crud.barani_sensors as db_service
from app.models.models import BaraniHelixSensors, BaraniWindSensors
from app.readings.schemas import HelixMessage, WindMessage
from app.logs.config_server_logs import server_logger

async def process_helix_message(db: AsyncSession, message: HelixMessage):
    server_logger.info(f"HELIX -- Received message: {message}")

    resp: BaraniHelixSensors = await db_service.create_barani_helix_reading(db, message)

    response = {"status": "success", "message": "helix reading created.", "details": f"{resp.__dict__}"}

    server_logger.info(response)

    return response


async def process_wind_message(db: AsyncSession, message: WindMessage):
    server_logger.info(f"WIND -- Received message: {message}")

    resp: BaraniWindSensors = await db_service.insert_barani_wind_reading(db, message)

    response = {"status": "success", "message": "wind reading created.", "details": f"{resp.__dict__}"}

    server_logger.info(response)

    return response


async def process_get_sensor_by_serial_number(db: AsyncSession, sn: str):
    server_logger.info(f"HELIX -- GET Received, serial number: {sn}")

    resp = await db_service.get_sensor_by_serial_number(db, sn)

    response = {"status": "success", "message": "Sensor readings returned.", "details": f"{resp.__dict__}"}

    server_logger.info(response)

    return response
