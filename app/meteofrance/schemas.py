from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MeteoFranceInfrahoraireMessage(BaseModel):
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    geo_id_insee: str = Field(..., description="Geographical ID (INSEE code)")
    reference_time: datetime = Field(..., description="Reference time of the measurement")
    insert_time: datetime = Field(..., description="Time when data was inserted")
    validity_time: datetime = Field(..., description="Time when data is valid")
    t: float = Field(..., description="Temperature in Kelvin")
    td: float = Field(..., description="Dew point temperature in Kelvin")
    u: int = Field(..., description="Humidity percentage")
    dd: int = Field(..., description="Wind direction in degrees")
    ff: float = Field(..., description="Wind speed in m/s")
    dxi10: Optional[int] = Field(None, description="Wind direction at 10 meters")
    fxi10: Optional[float] = Field(None, description="Maximum wind speed at 10 meters")
    rr_per: float = Field(..., description="Rainfall amount at 6 minutes in mm")
    t_10: float = Field(..., description="Temperature at 10cm depth below ground (Kelvin)")
    t_20: float = Field(..., description="Temperature at 20cm depth below ground (Kelvin)")
    t_50: float = Field(..., description="Temperature at 50cm depth below ground (Kelvin)")
    t_100: float = Field(..., description="Temperature at 100cm depth below ground (Kelvin)")
    vv: int = Field(..., description="Visibility in meters")
    etat_sol: Optional[str] = Field(None, description="Ground state (nullable) code")
    sss: int = Field(..., description="Snowfall in meters")
    insolh: int = Field(..., description="Sunshine duration in minutes")
    ray_glo01: int = Field(..., description="Global radiation (J/m²)")
    pres: int = Field(..., description="Atmospheric pressure at station level (Pa)")
    pmer: int = Field(..., description="Mean sea-level pressure (Pa)")

