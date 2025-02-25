from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.campbell.schemas import CampbellMessage
from app.models.models import CampbellSensors


async def create_campbell_reading(db: AsyncSession, sensor_reading: CampbellMessage):
    
    new_sensor = CampbellSensors(
        timestamp=sensor_reading.timestamp,
        air_temp_avg=sensor_reading.air_temp_avg,
        batt_voltage_avg=sensor_reading.batt_voltage_avg,
        bp_mbar_avg=sensor_reading.bp_mbar_avg,
        dew_point_avg=sensor_reading.dew_point_avg,
        met_sens_status=sensor_reading.met_sens_status,
        ms60_irradiance_avg=sensor_reading.ms60_irradiance_avg,
        p_temp_avg=sensor_reading.p_temp_avg,
        rain_mm_tot=sensor_reading.rain_mm_tot,
        humidity=sensor_reading.humidity,
        wind_dir=sensor_reading.wind_dir,
        wind_speed=sensor_reading.wind_speed,
        created_at=datetime.now()  # Use the current timestamp for creation
    )
    db.add(new_sensor)

    await db.commit()