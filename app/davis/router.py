import math
import traceback
from datetime import datetime
from typing import Optional, Union
import metpy.calc as mpcalc

import httpx
from fastapi import APIRouter, HTTPException, Depends, Header
from metpy.units import units
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
import app.davis.service as davis_service
from app.db.session import get_db
from app.logs.config_server_logs import server_logger
from app.davis.schemas import DavisMessage, DavisMessage, BarometerMessage, GatewayQuectelHealthMessage, VantageProV2Message

router = APIRouter()

def api_key_dependency(x_api_key: str = Header(...)):
    if x_api_key != settings.DAVIS_INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized access.")
    return x_api_key


def parse_row_to_message(row) -> DavisMessage:
    timestamp = int(datetime.strptime(row.get("Date & Time"), "%m/%d/%Y %H:%M").timestamp())
    for key, value in row.items():
        if isinstance(value, float) and math.isnan(value):
            row[key] = None
    message = DavisMessage(
        station_id_uuid="c19d7da3-8e50-4e87-b1bc-fa7d9b9a70d8",
        generated_at=timestamp,
        station_id=175979,
        barometer_msg=BarometerMessage(
            lsid=685205,
            sensor_type=3,
            data_structure_type=9,
            tz_offset=3600,
            ts=timestamp,
            pressure_last=row.get("Barometer - mm Hg")
        ),
        gateway_msg=GatewayQuectelHealthMessage(
            lsid=685204,
            sensor_type=507,
            data_structure_type=14,
            ts=timestamp,
            tz_offset=3600,
            platform_id=12,
        ),
        vantagePro_msg=VantageProV2Message(
            lsid=685219,
            sensor_type=79,
            data_structure_type=6,
            ts=timestamp,
            tz_offset=3600,

            bar=row.get("Barometer - mm Hg"),
            bar_absolute=row.get("Barometer - mm Hg"),
            bar_trend=None,
            dew_point=row.get("Dew Point - °C"),
            et_day=row.get("ET - mm"),
            forecast_rule=None,
            forecast_desc=None,
            heat_index=row.get("Heat Index - °C"),
            hum_out=row.get("Hum - %"),
            rain_15_min_clicks=None,
            rain_15_min_in=None,
            rain_15_min_mm=None,
            rain_60_min_clicks=None,
            rain_60_min_in=None,
            rain_60_min_mm=None,
            rain_24_hr_clicks=None,
            rain_24_hr_in=None,
            rain_24_hr_mm=None,
            rain_day_clicks=None,
            rain_day_in=None,
            rain_day_mm=None,
            rain_rate_clicks=None,
            rain_rate_in=None,
            rain_rate_mm=row.get("Rain Rate - mm/h"),
            rain_storm_clicks=None,
            rain_storm_in=None,
            rain_storm_mm=None,
            rain_storm_start_date=None,  # Seconds
            solar_rad=row.get("Solar Rad - W/m^2"),
            temp_out=row.get("Temp - °C"),
            thsw_index=row.get("THSW Index - °C"),
            uv=None if row.get("UV Index") == "--" else row.get("UV - %"),
            wind_chill=row.get("Wind Chill - °C"),
            wind_dir=direction_to_angle(row.get("Wind Direction")),
            wind_dir_of_gust_10_min=direction_to_angle(row.get("High Wind Direction")),
            wind_gust_10_min=direction_to_angle(row.get("High Wind Speed - km/h")),
            wind_speed=row.get("Wind Speed - km/h"),
            wind_speed_2_min=None,
            wind_speed_10_min=None,
            wet_bulb=row.get("Wet Bulb - °C")
        )
    )
    return message

@router.get("/receive_message/")
async def receive_message(api_key: str = Depends(api_key_dependency), db: AsyncSession = Depends(get_db)):
    import pandas as pd

    file_path = "app/davis/upload_data/second_year_davis.csv"

    chunk_size = 1000
    count = 0
    for chunk in pd.read_csv(file_path, chunksize=chunk_size, encoding="ISO-8859-1"):
        for _, row in chunk.iterrows():
            row_ = row.to_dict()
            print(row_)
            try:
                message: DavisMessage = parse_row_to_message(row=row_)
                server_logger.info(f"Received message with station_id: {message.station_id} and UUID: {message.station_id_uuid}")
            except Exception as e:
                server_logger.error(f"ERROR CODE 500 - Error parsing Davis response: {str(e)}")
                server_logger.error(row_)
                raise HTTPException(status_code=500, detail=str(e))
            print(f"Message ts {message.generated_at}, with success.")
            count += 1
            try:
                db_resp = await davis_service.process_davis_message(db, message)
            except Exception as e:
                server_logger.error(f"ERROR CODE 500 - Error processing Davis message: {str(e)}")
                server_logger.error("".join(traceback.format_exception(None, e, e.__traceback__)))
                server_logger.error(f"Error during Davis scheduled task: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            server_logger.info(db_resp)
    print(f"Count: {count}")
    # async with (httpx.AsyncClient() as client):
    #     external_api_uri = (f"https://{settings.DAVIS_EXTERNAL_API_URI}{settings.DAVIS_STATION_ID}"
    #                         f"?station-id={settings.DAVIS_STATION_ID}&api-key={settings.DAVIS_EXTERNAL_API_KEY}")
    #     headers = {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    #         'x-api-secret': f"{settings.DAVIS_EXTERNAL_API_SECRET}",
    #     }
    #     response = await client.get(external_api_uri, headers=headers)
    #
    #     if response.status_code != 200:
    #         error = f"DAVIS -- ERROR CODE 500 - Failed to fetch data from the external API"
    #         server_logger.error(error)
    #         raise HTTPException(status_code=500, detail=error)
    #
    #     response_data = response.json()
    #     try:
    #         message: DavisMessage = consume_message(response_data)
    #         server_logger.info(f"Received message with station_id: {message.station_id} and UUID: {message.station_id_uuid}")
    #     except Exception as e:
    #         server_logger.error(f"ERROR CODE 500 - Error parsing Davis response: {str(e)}")
    #         raise HTTPException(status_code=500, detail=str(e))
    #
    #     try:
    #         db_resp = await davis_service.process_davis_message(db, message)
    #     except Exception as e:
    #         server_logger.error(f"ERROR CODE 500 - Error processing Davis message: {str(e)}")
    #         server_logger.error("".join(traceback.format_exception(None, e, e.__traceback__)))
    #         server_logger.error(f"Error during Davis scheduled task: {e}")
    #         raise HTTPException(status_code=500, detail=str(e))
    #
    #     server_logger.debug({"status": "success", "station_id": message.station_id, "msg": db_resp})
    return {"status": "success", "station_id": message.station_id, "msg": message}

def consume_message(message)->DavisMessage:
    davis_message = DavisMessage(
        station_id_uuid=message['station_id_uuid'],
        generated_at=message['generated_at'],
        station_id=message['station_id'],
        barometer_msg=BarometerMessage(
            lsid=message['sensors'][2]['lsid'],
            sensor_type=message['sensors'][2]['sensor_type'],
            data_structure_type=message['sensors'][2]['data_structure_type'],
            tz_offset=message['sensors'][2]['data'][0]['tz_offset'],
            ts=message['sensors'][2]['data'][0]['ts'],
            bar_trend_3_hr=message['sensors'][2]['data'][0]['bar_trend_3_hr'],
            pressure_last=pressure_unit_conversion(message['sensors'][2]['data'][0]['pressure_last'])
        ),
        gateway_msg=GatewayQuectelHealthMessage(
            lsid=message['sensors'][1]['lsid'],
            sensor_type=message['sensors'][1]['sensor_type'],
            data_structure_type=message['sensors'][1]['data_structure_type'],
            ts=message['sensors'][1]['data'][0]['ts'],
            tz_offset=message['sensors'][1]['data'][0]['tz_offset'],
            iss_solar_panel_voltage=message['sensors'][1]['data'][0]['iss_solar_panel_voltage'],
            last_gps_reading_timestamp=message['sensors'][1]['data'][0]['last_gps_reading_timestamp'],
            resyncs=message['sensors'][1]['data'][0]['resyncs'],
            transmitter_battery_state=message['sensors'][1]['data'][0]['transmitter_battery_state'],
            crc_errors=message['sensors'][1]['data'][0]['crc_errors'],
            tiva_application_firmware_version=message['sensors'][1]['data'][0]['tiva_application_firmware_version'],
            lead_acid_battery_voltage=message['sensors'][1]['data'][0]['lead_acid_battery_voltage'],
            iss_transmitter_battery_voltage=message['sensors'][1]['data'][0]['iss_transmitter_battery_voltage'],
            beacon_interval=message['sensors'][1]['data'][0]['beacon_interval'],
            davistalk_rssi=message['sensors'][1]['data'][0]['davistalk_rssi'],
            solar_panel_voltage=message['sensors'][1]['data'][0]['solar_panel_voltage'],
            rank=message['sensors'][1]['data'][0]['rank'],
            false_wakeup_rssi=message['sensors'][1]['data'][0]['false_wakeup_rssi'],
            cell_id=message['sensors'][1]['data'][0]['cell_id'],
            longitude=message['sensors'][1]['data'][0]['longitude'],
            power_percentage_mcu=message['sensors'][1]['data'][0]['power_percentage_mcu'],
            mcc_mnc=message['sensors'][1]['data'][0]['mcc_mnc'],
            iss_super_cap_voltage=message['sensors'][1]['data'][0]['iss_super_cap_voltage'],
            false_wakeup_count=message['sensors'][1]['data'][0]['false_wakeup_count'],
            etx=message['sensors'][1]['data'][0]['etx'],
            number_of_neighbors=message['sensors'][1]['data'][0]['number_of_neighbors'],
            last_parent_rtt_ping=message['sensors'][1]['data'][0]['last_parent_rtt_ping'],
            bootloader_version=message['sensors'][1]['data'][0]['bootloader_version'],
            cme=message['sensors'][1]['data'][0]['cme'],
            cc1310_firmware_version=message['sensors'][1]['data'][0]['cc1310_firmware_version'],
            power_percentage_rx=message['sensors'][1]['data'][0]['power_percentage_rx'],
            good_packet_streak=message['sensors'][1]['data'][0]['good_packet_streak'],
            rpl_parent_node_id=message['sensors'][1]['data'][0]['rpl_parent_node_id'],
            afc_setting=message['sensors'][1]['data'][0]['afc_setting'],
            overall_access_technology=message['sensors'][1]['data'][0]['overall_access_technology'],
            cell_channel=message['sensors'][1]['data'][0]['cell_channel'],
            noise_floor_rssi=message['sensors'][1]['data'][0]['noise_floor_rssi'],
            latitude=message['sensors'][1]['data'][0]['latitude'],
            cereg=message['sensors'][1]['data'][0]['cereg'],
            last_cme_error_timestamp=message['sensors'][1]['data'][0]['last_cme_error_timestamp'],
            bluetooth_firmware_version=message['sensors'][1]['data'][0]['bluetooth_firmware_version'],
            location_area_code=message['sensors'][1]['data'][0]['location_area_code'],
            link_layer_packets_received=message['sensors'][1]['data'][0]['link_layer_packets_received'],
            reception_percent=message['sensors'][1]['data'][0]['reception_percent'],
            rx_bytes=message['sensors'][1]['data'][0]['rx_bytes'],
            link_uptime=message['sensors'][1]['data'][0]['link_uptime'],
            creg_cgreg=message['sensors'][1]['data'][0]['creg_cgreg'],
            health_version=message['sensors'][1]['data'][0]['health_version'],
            inside_box_temp=fahrenheit_to_celsius(message['sensors'][1]['data'][0]['inside_box_temp']),
            tx_bytes=message['sensors'][1]['data'][0]['tx_bytes'],
            elevation=message['sensors'][1]['data'][0]['elevation'],
            power_percentage_tx=message['sensors'][1]['data'][0]['power_percentage_tx'],
            rssi=message['sensors'][1]['data'][0]['rssi'],
            last_rx_rssi=message['sensors'][1]['data'][0]['last_rx_rssi'],
            rpl_mode=message['sensors'][1]['data'][0]['rpl_mode'],
            uptime=message['sensors'][1]['data'][0]['uptime'],
            platform_id=message['sensors'][1]['data'][0]['platform_id']
        ),
        vantagePro_msg=VantageProV2Message(
            lsid=message['sensors'][0]['lsid'],
            sensor_type=message['sensors'][0]['sensor_type'],
            data_structure_type=message['sensors'][0]['data_structure_type'],
            ts=message['sensors'][0]['data'][0]['ts'],
            tz_offset=message['sensors'][0]['data'][0]['tz_offset'],
            bar=pressure_unit_conversion(message['sensors'][0]['data'][0]['bar']),
            bar_absolute=pressure_unit_conversion(message['sensors'][0]['data'][0]['bar_absolute']),
            bar_trend=message['sensors'][0]['data'][0]['bar_trend'],
            dew_point=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['dew_point']),
            et_day=message['sensors'][0]['data'][0]['et_day'],
            forecast_rule=message['sensors'][0]['data'][0]['forecast_rule'],
            forecast_desc=message['sensors'][0]['data'][0]['forecast_desc'],
            heat_index=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['heat_index']),
            hum_out=message['sensors'][0]['data'][0]['hum_out'],
            rain_15_min_clicks=message['sensors'][0]['data'][0]['rain_15_min_clicks'],
            rain_15_min_in=message['sensors'][0]['data'][0]['rain_15_min_in'],
            rain_15_min_mm=message['sensors'][0]['data'][0]['rain_15_min_mm'],
            rain_60_min_clicks=message['sensors'][0]['data'][0]['rain_60_min_clicks'],
            rain_60_min_in=message['sensors'][0]['data'][0]['rain_60_min_in'],
            rain_60_min_mm=message['sensors'][0]['data'][0]['rain_60_min_mm'],
            rain_24_hr_clicks=message['sensors'][0]['data'][0]['rain_24_hr_clicks'],
            rain_24_hr_in=message['sensors'][0]['data'][0]['rain_24_hr_in'],
            rain_24_hr_mm=message['sensors'][0]['data'][0]['rain_24_hr_mm'],
            rain_day_clicks=message['sensors'][0]['data'][0]['rain_day_clicks'],
            rain_day_in=message['sensors'][0]['data'][0]['rain_day_in'],
            rain_day_mm=message['sensors'][0]['data'][0]['rain_day_mm'],
            rain_rate_clicks=message['sensors'][0]['data'][0]['rain_rate_clicks'],
            rain_rate_in=message['sensors'][0]['data'][0]['rain_rate_in'],
            rain_rate_mm=message['sensors'][0]['data'][0]['rain_rate_mm'],
            rain_storm_clicks=message['sensors'][0]['data'][0]['rain_storm_clicks'],
            rain_storm_in=message['sensors'][0]['data'][0]['rain_storm_in'],
            rain_storm_mm=message['sensors'][0]['data'][0]['rain_storm_mm'],
            rain_storm_start_date=message['sensors'][0]['data'][0]['rain_storm_start_date'],
            solar_rad=message['sensors'][0]['data'][0]['solar_rad'],
            temp_out=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['temp_out']),
            thsw_index=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['thsw_index']),
            uv=message['sensors'][0]['data'][0]['uv'],
            wind_chill=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['wind_chill']),
            wind_dir=direction_to_angle(message['sensors'][0]['data'][0]['wind_dir']),
            wind_dir_of_gust_10_min=message['sensors'][0]['data'][0]['wind_dir_of_gust_10_min'],
            wind_gust_10_min=mph_to_kmh(message['sensors'][0]['data'][0]['wind_gust_10_min']),
            wind_speed=mph_to_kmh(message['sensors'][0]['data'][0]['wind_speed']),
            wind_speed_2_min=mph_to_kmh(message['sensors'][0]['data'][0]['wind_speed_2_min']),
            wind_speed_10_min=mph_to_kmh(message['sensors'][0]['data'][0]['wind_speed_10_min']),
            wet_bulb=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['wet_bulb'])
        )
    )
    return davis_message

def pressure_unit_conversion(pressure_in: float) -> float:
    """
    Get pressure in inch - Hg and turn into mm - Hg
    1 mmHg = 133.322 pascals (Pa)
    1 inHg = 3386.39 pascals (Pa)
    mmHg value x 133.322 Pa = inHg value x 3386.39 Pa
    mmHg value = inHg value x 25.4

    :param pressure_in:
    :return:
    """
    return float(pressure_in * 25.4)

def fahrenheit_to_celsius(temperature_f: Optional[Union[float, int]]) -> Optional[Union[float, int]]:
    """
    Get temperature in Fahrenheit (°F) and
    convert to Celsius (°C)
    °C = (°F - 32) ÷ (9/5) or °C = (°F - 32) ÷ (1.8)

    :param temperature_f:
    :return:
    """
    if type(temperature_f) is float:
        return float((temperature_f * units.Fahrenheit).to(units.Celsius).magnitude)
        # return float(float(temperature_f - 32.0) / 1.8)
    elif type(temperature_f) is int:
        return round((temperature_f * units.Fahrenheit).to(units.Celsius).magnitude)
        # return int(float(temperature_f - 32.0) / 1.8)

def direction_to_angle(wind_dir_d: Optional[Union[str, int]]) -> Optional[int]:
    """
    Converts compass to degrees unit using metpy. Compass can be NNE, WSW, SSE etc.
    Numbers are rounded to integer for consistency. If the value received is in integer,
    the absolute number is uploaded. For reference:
    "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
    "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
    "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
    "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5

    :param wind_dir_d:
    :return:
    """
    if type(wind_dir_d) is int:
        return wind_dir_d
    elif type(wind_dir_d) is str:
        angle_units = mpcalc.parse_angle(wind_dir_d)
        return round(angle_units.magnitude)

def mph_to_kmh(mph_val: Optional[int]) -> Optional[int]:
    """
    Convert mph (miles per hour) to km/h (kilometers per hour)
    1 mile per hour = 1.609344 kilometers per hour

    :param mph_val:
    :return:
    """
    return round((mph_val * units.mph).to(units.km / units.hour).magnitude)