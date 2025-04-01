from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

import app.crud.barani_sensors as db_service
from app.models.models import BaraniHelixSensors, BaraniWindSensors
from app.barani.schemas import HelixMessage, WindMessage
from app.logs.config_server_logs import server_logger

async def process_helix_message(db: AsyncSession, message: HelixMessage):
    server_logger.info(f"HELIX -- Received message: {message}")

    message = normalize_helix_message(message)

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

    response = {"status": "success", "message": "Sensor barani returned.", "details": f"{resp.__dict__}"}

    server_logger.info(response)

    return response

def normalize_helix_message(message: HelixMessage)->HelixMessage:
    copied = message.model_copy()

    if  copied.temperature and 173.15 < copied.temperature < 373.15:
        copied.temperature = kelvin_to_celsius(message.temperature)
        server_logger.info(f"HELIX -- Received message: Message.temperature modified to fix Kelvin values: "
                      f"{message.temperature} -> {copied.temperature}")

    if  copied.temperature_wetbulb and 173.15 < copied.temperature_wetbulb < 373.15:
        copied.temperature_wetbulb = kelvin_to_celsius(message.temperature_wetbulb)
        server_logger.info(f"HELIX -- Received message: Message.temperature_wetbulb modified to fix Kelvin values: "
                      f"{message.temperature_wetbulb} -> {copied.temperature_wetbulb}")

    if  copied.dew_point and 173.15 < copied.dew_point < 373.15:
        copied.dew_point = kelvin_to_celsius(message.dew_point)
        server_logger.info(f"HELIX -- Received message: Message.dew_point modified to fix Kelvin values: "
                      f"{message.dew_point} -> {copied.dew_point}")

    return copied

def kelvin_to_celsius(kelvin: Optional[float])->Optional[float]:
    """
    Converts Kelvin to Celsius.

    :param kelvin:
    :return:
    """
    return round(kelvin - 273.15, 2) if kelvin is not None else None