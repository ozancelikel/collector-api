from typing import Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class VantageProV2Message(BaseModel):
    lsid: int
    sensor_type: int
    data_structure_type: int
    ts: int
    tz_offset: int

    bar: Optional[float] = None
    bar_absolute: Optional[float] = None
    bar_trend: Optional[int] = None
    dew_point: Optional[int] = None
    et_day: Optional[float] = None
    forecast_rule: Optional[int] = None
    forecast_desc: Optional[str] = None
    heat_index: Optional[int] = None
    hum_out: Optional[int] = None
    rain_15_min_clicks: Optional[int] = None
    rain_15_min_in: Optional[float] = None
    rain_15_min_mm: Optional[float] = None
    rain_60_min_clicks: Optional[int] = None
    rain_60_min_in: Optional[float] = None
    rain_60_min_mm: Optional[float] = None
    rain_24_hr_clicks: Optional[int] = None
    rain_24_hr_in: Optional[float] = None
    rain_24_hr_mm: Optional[float] = None
    rain_day_clicks: Optional[int] = None
    rain_day_in: Optional[float] = None
    rain_day_mm: Optional[float] = None
    rain_rate_clicks: Optional[int] = None
    rain_rate_in: Optional[float] = None
    rain_rate_mm: Optional[float] = None
    rain_storm_clicks: Optional[int] = None
    rain_storm_in: Optional[float] = None
    rain_storm_mm: Optional[float] = None
    rain_storm_start_date: Optional[int] = None  # Seconds
    solar_rad: Optional[int] = None
    temp_out: Optional[float] = None
    thsw_index: Optional[int] = None
    uv: Optional[float] = None
    wind_chill: Optional[int] = None
    wind_dir: Optional[int] = None
    wind_dir_of_gust_10_min: Optional[int] = None
    wind_gust_10_min: Optional[int] = None
    wind_speed: Optional[int] = None
    wind_speed_2_min: Optional[float] = None
    wind_speed_10_min: Optional[float] = None
    wet_bulb: Optional[float] = None

class GatewayQuectelHealthMessage(BaseModel):
    lsid: int
    sensor_type: int
    data_structure_type: int
    ts: int
    tz_offset: int

    iss_solar_panel_voltage: Optional[float] = None
    last_gps_reading_timestamp: Optional[int] = None
    resyncs: Optional[int] = None
    transmitter_battery_state: Optional[int] = None
    crc_errors: Optional[int] = None
    tiva_application_firmware_version: Optional[int] = None
    lead_acid_battery_voltage: Optional[int] = None
    iss_transmitter_battery_voltage: Optional[float] = None
    beacon_interval: Optional[int] = None
    davistalk_rssi: Optional[int] = None
    solar_panel_voltage: Optional[int] = None
    rank: Optional[int] = None
    false_wakeup_rssi: Optional[int] = None
    cell_id: Optional[int] = None
    longitude: Optional[float] = None
    power_percentage_mcu: Optional[int] = None
    mcc_mnc: Optional[int] = None
    iss_super_cap_voltage: Optional[float] = None
    false_wakeup_count: Optional[int] = None
    etx: Optional[int] = None
    number_of_neighbors: Optional[int] = None
    last_parent_rtt_ping: Optional[int] = None
    bootloader_version: Optional[int] = None
    cme: Optional[int] = None
    cc1310_firmware_version: Optional[int] = None
    power_percentage_rx: Optional[int] = None
    good_packet_streak: Optional[int] = None
    rpl_parent_node_id: Optional[int] = None
    afc_setting: Optional[int] = None
    overall_access_technology: Optional[int] = None
    cell_channel: Optional[int] = None
    noise_floor_rssi: Optional[int] = None
    latitude: Optional[float] = None
    cereg: Optional[int] = None
    last_cme_error_timestamp: Optional[int] = None
    bluetooth_firmware_version: Optional[int] = None
    location_area_code: Optional[int] = None
    link_layer_packets_received: Optional[int] = None
    reception_percent: Optional[int] = None
    rx_bytes: Optional[int] = None
    link_uptime: Optional[int] = None
    creg_cgreg: Optional[int] = None
    health_version: Optional[int] = None
    inside_box_temp: Optional[float] = None
    tx_bytes: Optional[int] = None
    elevation: Optional[int] = None
    power_percentage_tx: Optional[int] = None
    rssi: Optional[int] = None
    last_rx_rssi: Optional[int] = None
    rpl_mode: Optional[int] = None
    uptime: Optional[int] = None
    platform_id: Optional[int] = None

class BarometerMessage(BaseModel):
    lsid: int
    sensor_type: int
    data_structure_type: int

    tz_offset: int
    ts: int
    bar_trend_3_hr: Optional[float] = None
    pressure_last: Optional[float] = None

class DavisMessage(BaseModel):
    station_id_uuid: str
    generated_at: int
    station_id: int

    barometer_msg: BarometerMessage
    gateway_msg: GatewayQuectelHealthMessage
    vantagePro_msg: VantageProV2Message


class HistoricMessage(BaseModel):
    start_time: int = Field(..., description="Unix timestamp (seconds)")
    end_time: int = Field(..., description="Unix timestamp (seconds)")

    @model_validator(mode='after')
    def check_time_diff(self) -> Self:
        if self.start_time is not None and (self.end_time - self.start_time) > 86400:
            raise RequestValidationError("Timestamps cannot be more than 24 hours apart.")
        return self

