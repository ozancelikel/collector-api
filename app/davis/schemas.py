from typing import List, Optional
from pydantic import BaseModel


class VantageProV2Message(BaseModel):
    lsid: int
    sensor_type: int
    data_structure_type: int

    ts: int
    tz_offset: int
    bar: float
    bar_absolute: float
    bar_trend: int
    dew_point: int
    et_day: float
    forecast_rule: int
    forecast_desc: str
    heat_index: int
    hum_out: int
    rain_15_min_clicks: int
    rain_15_min_in: float
    rain_15_min_mm: float
    rain_60_min_clicks: int
    rain_60_min_in: float
    rain_60_min_mm: float
    rain_24_hr_clicks: int
    rain_24_hr_in: float
    rain_24_hr_mm: float
    rain_day_clicks: int
    rain_day_in: float
    rain_day_mm: float
    rain_rate_clicks: int
    rain_rate_in: float
    rain_rate_mm: float
    rain_storm_clicks: int
    rain_storm_in: float
    rain_storm_mm: float
    rain_storm_start_date: Optional[int]  # Seconds
    solar_rad: int
    temp_out: float
    thsw_index: int
    uv: Optional[float]
    wind_chill: int
    wind_dir: int
    wind_dir_of_gust_10_min: int
    wind_gust_10_min: int
    wind_speed: int
    wind_speed_2_min: float
    wind_speed_10_min: float
    wet_bulb: float


class GatewayQuectelHealthMessage(BaseModel):
    lsid: int
    sensor_type: int
    data_structure_type: int

    ts: int
    tz_offset: int
    iss_solar_panel_voltage: Optional[float]
    last_gps_reading_timestamp: int
    resyncs: int
    transmitter_battery_state: int
    crc_errors: int
    tiva_application_firmware_version: int
    lead_acid_battery_voltage: int
    iss_transmitter_battery_voltage: Optional[float]
    beacon_interval: int
    davistalk_rssi: int
    solar_panel_voltage: int
    rank: int
    false_wakeup_rssi: int
    cell_id: int
    longitude: float
    power_percentage_mcu: int
    mcc_mnc: int
    iss_super_cap_voltage: Optional[float]
    false_wakeup_count: int
    etx: int
    number_of_neighbors: int
    last_parent_rtt_ping: int
    bootloader_version: int
    cme: int
    cc1310_firmware_version: int
    power_percentage_rx: int
    good_packet_streak: int
    rpl_parent_node_id: Optional[int]
    afc_setting: int
    overall_access_technology: int
    cell_channel: int
    noise_floor_rssi: int
    latitude: float
    cereg: int
    last_cme_error_timestamp: Optional[int]
    bluetooth_firmware_version: Optional[int]
    location_area_code: int
    link_layer_packets_received: int
    reception_percent: int
    rx_bytes: int
    link_uptime: int
    creg_cgreg: int
    health_version: int
    inside_box_temp: float
    tx_bytes: int
    elevation: int
    power_percentage_tx: int
    rssi: int
    last_rx_rssi: int
    rpl_mode: int
    uptime: int
    platform_id: int

class BarometerMessage(BaseModel):
    lsid: int
    sensor_type: int
    data_structure_type: int

    tz_offset: int
    ts: int
    bar_trend_3_hr: float
    pressure_last: float

class DavisMessage(BaseModel):
    station_id_uuid: str
    generated_at: int
    station_id: int

    barometer_msg: BarometerMessage
    gateway_msg: GatewayQuectelHealthMessage
    vantagePro_msg: VantageProV2Message