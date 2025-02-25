from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class CampbellMessage(BaseModel):
    timestamp: datetime
    air_temp_avg: Optional[float]
    batt_voltage_avg: Optional[float]
    bp_mbar_avg: Optional[float]
    dew_point_avg: Optional[float]
    met_sens_status: Optional[str]
    ms60_irradiance_avg: Optional[float]
    p_temp_avg: Optional[float]
    rain_mm_tot: Optional[float]
    humidity: Optional[float]
    wind_dir: Optional[float]
    wind_speed: Optional[float]

    class Config:
        orm_mode = True
