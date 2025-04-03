import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, PrimaryKeyConstraint, ForeignKey, Integer, BigInteger
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB

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
    wind_min10 = Column(Float)

    wdir_gust10 = Column(Float)
    wdir_stdev10 = Column(Float)
    wind_stdev10 = Column(Float)

    created_at = Column(DateTime)

    # composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('serial_number', 'timestamp'),
    )

class CampbellSensors(Base):
    __tablename__ = 'campbell_capu_di_muru'

    timestamp = Column(DateTime, primary_key=True)
    station_name = Column(String, ForeignKey('campbell_station.name'))
    air_temp_avg = Column(Float)
    batt_voltage_avg = Column(Float)
    bp_mbar_avg = Column(Float)
    dew_point_avg = Column(Float)
    met_sens_status = Column(String)
    ms60_irradiance_avg = Column(Float)
    p_temp_avg = Column(Float)
    rain_mm_tot = Column(Float)
    humidity = Column(Float)
    wind_dir = Column(Float)
    wind_speed = Column(Float)
    created_at = Column(DateTime)


class CampbellStation(Base):
    __tablename__ = "campbell_station"

    name = Column(String, primary_key=True, nullable=False)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)

class DavisStation(Base):
    __tablename__ = 'davis_station'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(Integer)
    station_id_uuid = Column(String)
    created_at = Column(DateTime, default=func.now())

    # Foreign key relationships
    barometer_reading = Column(UUID(as_uuid=True), ForeignKey('davis_barometer.id'))
    gatewayquectel_reading = Column(UUID(as_uuid=True), ForeignKey('davis_gatewayquectel.id'))
    vantagepro2_reading = Column(UUID(as_uuid=True), ForeignKey('davis_vantagepro2.id'))

    # Relationships with other tables
    barometer = relationship("DavisBarometer", backref="stations")
    gatewayquectel = relationship("DavisGatewayQuectel", backref="stations")
    vantagepro2 = relationship("DavisVantagePro2", backref="stations")

class DavisVantagePro2(Base):
    __tablename__ = 'davis_vantagepro2'

    id = Column(UUID(as_uuid=True), primary_key=True)
    lsid = Column(Integer)
    ts = Column(BigInteger, unique=True)
    tz_offset = Column(Integer)
    date = Column(DateTime)
    sensor_data_structure_id = Column(String, ForeignKey('davis_sensor_data_structure.id'))
    created_at = Column(DateTime, default=func.now())

    # Sensor data columns
    bar = Column(Float)
    bar_absolute = Column(Float)
    bar_trend = Column(Integer)
    dew_point = Column(Integer)
    et_day = Column(Float)
    forecast_rule = Column(Integer)
    forecast_desc = Column(String)
    heat_index = Column(Integer)
    hum_out = Column(Integer)
    rain_15_min_clicks = Column(Integer)
    rain_15_min_in = Column(Float)
    rain_15_min_mm = Column(Float)
    rain_60_min_clicks = Column(Integer)
    rain_60_min_in = Column(Float)
    rain_60_min_mm = Column(Float)
    rain_24_hr_clicks = Column(Integer)
    rain_24_hr_in = Column(Float)
    rain_24_hr_mm = Column(Float)
    rain_day_clicks = Column(Integer)
    rain_day_in = Column(Float)
    rain_day_mm = Column(Float)
    rain_rate_clicks = Column(Integer)
    rain_rate_in = Column(Float)
    rain_rate_mm = Column(Float)
    rain_storm_clicks = Column(Integer)
    rain_storm_in = Column(Float)
    rain_storm_mm = Column(Float)
    rain_storm_start_date = Column(Integer)  # Seconds
    solar_rad = Column(Integer)
    temp_out = Column(Float)
    thsw_index = Column(Integer)
    uv = Column(Float)
    wind_chill = Column(Integer)
    wind_dir = Column(Integer)
    wind_dir_of_gust_10_min = Column(Integer)
    wind_gust_10_min = Column(Integer)
    wind_speed = Column(Integer)
    wind_speed_2_min = Column(Float)
    wind_speed_10_min = Column(Float)
    wet_bulb = Column(Float)

class DavisGatewayQuectel(Base):
    __tablename__ = 'davis_gatewayquectel'

    id = Column(UUID(as_uuid=True), primary_key=True)
    lsid = Column(Integer)
    ts = Column(BigInteger, unique=True)
    tz_offset = Column(Integer)
    date = Column(DateTime)
    sensor_data_structure_id = Column(String, ForeignKey('davis_sensor_data_structure.id'))
    created_at = Column(DateTime, default=func.now())

    # Sensor data columns
    iss_solar_panel_voltage = Column(Float)
    last_gps_reading_timestamp = Column(BigInteger)
    resyncs = Column(Integer)
    transmitter_battery_state = Column(Integer)
    crc_errors = Column(Integer)
    tiva_application_firmware_version = Column(BigInteger)
    lead_acid_battery_voltage = Column(Integer)
    iss_transmitter_battery_voltage = Column(Float)
    beacon_interval = Column(Integer)
    davistalk_rssi = Column(Integer)
    solar_panel_voltage = Column(Integer)
    rank = Column(Integer)
    false_wakeup_rssi = Column(Integer)
    cell_id = Column(BigInteger)
    longitude = Column(Float)
    power_percentage_mcu = Column(Integer)
    mcc_mnc = Column(BigInteger)
    iss_super_cap_voltage = Column(Float)
    false_wakeup_count = Column(Integer)
    etx = Column(Integer)
    number_of_neighbors = Column(Integer)
    last_parent_rtt_ping = Column(Integer)
    bootloader_version = Column(BigInteger)
    cme = Column(Integer)
    cc1310_firmware_version = Column(BigInteger)
    power_percentage_rx = Column(Integer)
    good_packet_streak = Column(Integer)
    rpl_parent_node_id = Column(BigInteger)
    afc_setting = Column(Integer)
    overall_access_technology = Column(Integer)
    cell_channel = Column(BigInteger)
    noise_floor_rssi = Column(Integer)
    latitude = Column(Float)
    cereg = Column(Integer)
    last_cme_error_timestamp = Column(BigInteger)
    bluetooth_firmware_version = Column(BigInteger)
    location_area_code = Column(Integer)
    link_layer_packets_received = Column(Integer)
    reception_percent = Column(Integer)
    rx_bytes = Column(BigInteger)
    link_uptime = Column(BigInteger)
    creg_cgreg = Column(Integer)
    health_version = Column(Integer)
    inside_box_temp = Column(Float)
    tx_bytes = Column(BigInteger)
    elevation = Column(Integer)
    power_percentage_tx = Column(Integer)
    rssi = Column(Integer)
    last_rx_rssi = Column(Integer)
    rpl_mode = Column(Integer)
    uptime = Column(BigInteger)
    platform_id = Column(Integer)

class DavisBarometer(Base):
    __tablename__ = 'davis_barometer'

    id = Column(UUID(as_uuid=True), primary_key=True)
    lsid = Column(Integer)
    ts = Column(BigInteger, unique=True)
    tz_offset = Column(Integer)
    date = Column(DateTime)
    sensor_data_structure_id = Column(String, ForeignKey('davis_sensor_data_structure.id'))
    created_at = Column(DateTime, default=func.now())

    # Sensor data columns
    pressure_last = Column(Float)
    bar_trend_3_hr = Column(Float)

class DavisSensorDataStructure(Base):
    __tablename__ = 'davis_sensor_data_structure'

    id = Column(VARCHAR, primary_key=True)
    sensor_type = Column(Integer)
    data_structure_type = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    product_name = Column(String)
    data_structure = Column(JSONB)

class MeteoFranceData(Base):
    __tablename__ = 'meteo_france_data'

    geo_id_insee = Column(String, nullable=True)
    reference_time = Column(DateTime, nullable=False)
    insert_time = Column(DateTime, nullable=True)
    validity_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    t = Column(Float, nullable=True)
    td = Column(Float, nullable=True)
    u = Column(Integer, nullable=True)
    dd = Column(Integer, nullable=True)
    ff = Column(Float, nullable=True)
    dxi10 = Column(Integer, nullable=True)
    fxi10 = Column(Float, nullable=True)
    rr_per = Column(Float, nullable=True)
    t_10 = Column(Float, nullable=True)
    t_20 = Column(Float, nullable=True)
    t_50 = Column(Float, nullable=True)
    t_100 = Column(Float, nullable=True)
    vv = Column(Integer, nullable=True)
    etat_sol = Column(String, nullable=True)
    sss = Column(Integer, nullable=True)
    insolh = Column(Integer, nullable=True)
    ray_glo01 = Column(Integer, nullable=True)
    pres = Column(Integer, nullable=True)
    pmer = Column(Integer, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('geo_id_insee', 'reference_time'),
    )

    @classmethod
    def from_dict(cls, data: dict):
        """
        Class method to create an instance from the dictionary (e.g., from an incoming message).
        Ensures that datetime fields are converted to naive datetimes (without timezone).
        """

        def make_naive(dt):
            return dt.replace(tzinfo=None) if isinstance(dt, datetime) and dt.tzinfo else dt

        return cls(
            lat=data["lat"],
            lon=data["lon"],
            geo_id_insee=data["geo_id_insee"],
            reference_time=make_naive(data["reference_time"]),
            insert_time=make_naive(data["insert_time"]),
            validity_time=make_naive(data["validity_time"]),
            t=data["t"],
            td=data["td"],
            u=data["u"],
            dd=data["dd"],
            ff=data["ff"],
            dxi10=data.get("dxi10"),
            fxi10=data.get("fxi10"),
            rr_per=data["rr_per"],
            t_10=data["t_10"],
            t_20=data["t_20"],
            t_50=data["t_50"],
            t_100=data["t_100"],
            vv=data["vv"],
            etat_sol=data.get("etat_sol"),
            sss=data["sss"],
            insolh=data["insolh"],
            ray_glo01=data["ray_glo01"],
            pres=data["pres"],
            pmer=data["pmer"]
        )