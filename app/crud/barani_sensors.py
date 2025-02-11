from datetime import datetime

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import BaraniHelixSensors, BaraniWindSensors
from app.readings.schemas import HelixMessage, WindMessage


async def get_sensor_by_serial_number(db: AsyncSession, serial_number: str):
    result = await db.execute(
        select(BaraniHelixSensors).filter(BaraniHelixSensors.serial_number == serial_number)
    )
    return result.scalars().first()


async def create_barani_helix_reading(db: AsyncSession, sensor_reading: HelixMessage):

    timestamp = sensor_reading.timestamp
    if isinstance(timestamp, datetime):
        timestamp = timestamp.replace(tzinfo=None)
    else:
        timestamp = datetime.fromisoformat(timestamp).replace(
            tzinfo=None)

    new_reading = BaraniHelixSensors(
        timestamp=timestamp,
        serial_number=sensor_reading.serial_number,
        rain=sensor_reading.rain,
        battery=sensor_reading.battery,
        dew_point=sensor_reading.dew_point,
        humidity=sensor_reading.humidity,
        pressure=sensor_reading.pressure,
        irradiation=sensor_reading.irradiation,
        temperature=sensor_reading.temperature,
        rainfall_rate_max=sensor_reading.rainfall_rate_max,
        temperature_wetbulb=sensor_reading.temperature_wetbulb,
        created_at=datetime.now()
    )

    db.add(new_reading)
    await db.commit()
    await db.refresh(new_reading)
    return new_reading


async def insert_barani_wind_reading(db: AsyncSession, wind_reading: WindMessage):
    timestamp = wind_reading.timestamp
    if isinstance(timestamp, datetime):
        timestamp = timestamp.replace(tzinfo=None)
    else:
        timestamp = datetime.fromisoformat(timestamp).replace(
            tzinfo=None)

    new_reading = BaraniWindSensors(
        timestamp=timestamp,
        serial_number=wind_reading.serial_number,
        battery=wind_reading.battery,
        wdir_avg10=wind_reading.wdir_avg10,
        wdir_max10=wind_reading.wdir_max10,
        wdir_min10=wind_reading.wdir_min10,
        wind_avg10=wind_reading.wind_avg10,
        wind_max10=wind_reading.wind_max10,
        wind_gust10=wind_reading.wind_gust10,
        wdir_stdev10=wind_reading.wdir_stdev10,
        wind_stdev10=wind_reading.wind_stdev10,
        created_at=datetime.utcnow(),
    )

    db.add(new_reading)
    await db.commit()
    await db.refresh(new_reading)
    return new_reading
