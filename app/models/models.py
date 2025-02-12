from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaraniHelixSensors(Base):
    __tablename__ = 'barani_helix_sensors'

    serial_number = Column(String, primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    rain = Column(Float)
    battery = Column(Float)
    dew_point = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    irradiation = Column(Float)
    temperature = Column(Float)
    rainfall_rate_max = Column(Float)
    temperature_wetbulb = Column(Float)
    created_at = Column(DateTime)


class BaraniWindSensors(Base):
    __tablename__ = 'barani_wind_sensors'

    serial_number = Column(String, primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    battery = Column(Float)
    wdir_avg10 = Column(Float)
    wdir_max10 = Column(Float)
    wdir_min10 = Column(Float)
    wind_avg10 = Column(Float)
    wind_max10 = Column(Float)
    wind_gust10 = Column(Float)
    wdir_stdev10 = Column(Float)
    wind_stdev10 = Column(Float)
    created_at = Column(DateTime)

