from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union


class HelixMessage(BaseModel):
    timestamp: Union[str, datetime] = Field(..., alias="time", example="1738143000000")
    serial_number: str = Field(..., alias="sn", example="2110XX001")

    rain: Optional[float] = Field(..., alias="Rain", example=None)
    battery: Optional[float] = Field(..., alias="Battery", example=None)
    dew_point: Optional[float] = Field(..., alias="DewPoint", example=None)
    humidity: Optional[float] = Field(..., alias="Humidity", example=None)
    pressure: Optional[float] = Field(..., alias="Pressure", example=None)
    irradiation: Optional[float] = Field(..., alias="Irradiation", example=None)
    temperature: Optional[float] = Field(..., alias="Temperature", example=None)
    rainfall_rate_max: Optional[float] = Field(..., alias="Rainfall_rate_max", example=None)
    temperature_wetbulb: Optional[float] = Field(..., alias="Temperature_wetbulb_stull2011_C", example=None)


"""
    @classmethod
    @field_validator("timestamp", mode="before")
    def format_timestamp(cls,  value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")
"""


class WindMessage(BaseModel):
    timestamp: Union[str, datetime] = Field(..., alias="time", example="1738143000000")
    serial_number: str = Field(..., alias="sn", example="2110XX001")
    battery: Optional[float] = Field(..., alias="Battery", example=None)

    wdir_avg10: Optional[float] = Field(..., alias="Wdir_Avg10", example=None)
    wdir_max10: Optional[float] = Field(..., alias="Wdir_Max10", example=None)
    wdir_min10: Optional[float] = Field(..., alias="Wdir_Min10", example=None)

    wind_avg10: Optional[float] = Field(..., alias="Wind_Avg10", example=None)
    wind_max10: Optional[float] = Field(..., alias="Wind_Max10", example=None)
    wind_min10: Optional[float] = Field(..., alias="Wind_Min10", example=None)

    wdir_gust10: Optional[float] = Field(..., alias="Wdir_Gust10", example=None)
    wdir_stdev10: Optional[float] = Field(..., alias="Wdir_Stdev10", example=None)
    wind_stdev10: Optional[float] = Field(..., alias="Wind_Stdev10", example=None)


"""
    @classmethod
    @field_validator("timestamp", mode="before")
    def format_timestamp(cls, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")
"""