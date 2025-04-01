import traceback
from typing import Optional, Union
import metpy.calc as mpcalc

import httpx
from fastapi import APIRouter, HTTPException, Depends
from metpy.units import units
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
import app.davis.service as davis_service
from app.db.session import get_db
from app.logs.config_server_logs import server_logger
from app.davis.schemas import DavisMessage, BarometerMessage, GatewayQuectelHealthMessage, VantageProV2Message, \
    HistoricMessage
from app.authentication import api_token

router = APIRouter()


def rebuild_message(vantagepro2: dict, gateway: dict, baro: dict, msg: dict) -> dict:
    return {
        "station_id_uuid": msg.get("station_id_uuid"),
        "generated_at": msg.get("generated_at"),
        "station_id": msg.get("station_id"),
        "sensors": [
            {
                "lsid": msg.get("sensors")[0].get("lsid"),
                "sensor_type": msg.get("sensors")[0].get("sensor_type"),
                "data_structure_type": msg.get("sensors")[0].get("data_structure_type"),
                "data": [vantagepro2]
            },
            {
                "lsid": msg.get("sensors")[1].get("lsid"),
                "sensor_type": msg.get("sensors")[1].get("sensor_type"),
                "data_structure_type": msg.get("sensors")[1].get("data_structure_type"),
                "data": [gateway]
            },
            {
                "lsid": msg.get("sensors")[2].get("lsid"),
                "sensor_type": msg.get("sensors")[2].get("sensor_type"),
                "data_structure_type": msg.get("sensors")[2].get("data_structure_type"),
                "data": [baro]
            }
        ]
    }


@router.post("/receive_historic/", dependencies=[Depends(api_token)])
async def receive_historic(historic: HistoricMessage, db: AsyncSession = Depends(get_db)):
    async with (httpx.AsyncClient() as client):
        external_api_uri = (f"https://{settings.DAVIS_HISTORIC_API_URI}{settings.DAVIS_STATION_ID}"
                            f"?station-id={settings.DAVIS_STATION_ID}&api-key={settings.DAVIS_EXTERNAL_API_KEY}"
                            f"&start-timestamp={historic.start_time}&end-timestamp={historic.end_time}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'x-api-secret': f"{settings.DAVIS_EXTERNAL_API_SECRET}",
        }
        try:
            response = await client.get(external_api_uri, headers=headers)
        except Exception as e:
            server_logger.error(f"ERROR CODE 500 - Error parsing Davis response: {str(e)}")
        if response.status_code != 200:
            error = f"DAVIS -- ERROR CODE 500 - Failed to fetch data from the historic API"
            print(response.status_code)
            server_logger.error(error)
            raise HTTPException(status_code=500, detail=error)

        response_data = response.json()
        response_data.get("sensors")[0].get("data")
        vantagepro2_list = response_data.get("sensors")[0].get("data")
        gateway_list = response_data.get("sensors")[1].get("data")
        server_logger.info(f"Len of gateway list: {len(gateway_list)}")
        barometer_list = response_data.get("sensors")[2].get("data")
        for i in range(len(vantagepro2_list)):
            for j in range(len(gateway_list) - 1):
                if gateway_list[j].get("ts") <= vantagepro2_list[i].get("ts") < gateway_list[j+1].get("ts"):
                    gateway = gateway_list[j]
                elif vantagepro2_list == gateway_list[j+1].get("ts"):
                    gateway = gateway_list[j+1]
                elif j == len(gateway_list) - 2:
                    gateway = gateway_list[j]
                else:
                    continue
                break
            new_message = rebuild_message(vantagepro2_list[i], gateway, barometer_list[i], response_data)
            try:
                db_resp = await davis_service.process_davis_message(db, consume_historic_msg(new_message))
            except Exception as e:
                server_logger.error(f"ERROR CODE 500 - Error processing Davis message: {str(e)}")
                server_logger.error("".join(traceback.format_exception(None, e, e.__traceback__)))
                server_logger.error(f"Error during Davis scheduled task: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            server_logger.debug({"status": "success", "msg": db_resp})

        return {"status": "success", "msg": "Uploaded docs with success."}


@router.get("/receive_message/", dependencies=[Depends(api_token)])
async def receive_message(db: AsyncSession = Depends(get_db)):
    async with (httpx.AsyncClient() as client):
        external_api_uri = (f"https://{settings.DAVIS_EXTERNAL_API_URI}{settings.DAVIS_STATION_ID}"
                            f"?station-id={settings.DAVIS_STATION_ID}&api-key={settings.DAVIS_EXTERNAL_API_KEY}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'x-api-secret': f"{settings.DAVIS_EXTERNAL_API_SECRET}",
        }
        response = await client.get(external_api_uri, headers=headers)

        if response.status_code != 200:
            error = f"DAVIS -- ERROR CODE 500 - Failed to fetch data from the external API"
            server_logger.error(error)
            raise HTTPException(status_code=500, detail=error)

        response_data = response.json()
        try:
            message: DavisMessage = consume_current_msg(response_data)
            server_logger.info(f"Received message with station_id: {message.station_id} and UUID: {message.station_id_uuid}")
        except Exception as e:
            server_logger.error(f"ERROR CODE 500 - Error parsing Davis response: {str(e)}")
            server_logger.error("".join(traceback.format_exception(None, e, e.__traceback__)))
            raise HTTPException(status_code=500, detail=str(e))

        try:
            db_resp = await davis_service.process_davis_message(db, message)
        except Exception as e:
            server_logger.error(f"ERROR CODE 500 - Error processing Davis message: {str(e)}")
            server_logger.error("".join(traceback.format_exception(None, e, e.__traceback__)))
            server_logger.error(f"Error during Davis scheduled task: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        server_logger.debug({"status": "success", "station_id": message.station_id, "msg": db_resp})
    return {"status": "success", "station_id": message.station_id, "msg": message}

def consume_current_msg(message)->DavisMessage:
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
            bar_trend_3_hr=inhg_to_mmhg(message['sensors'][2]['data'][0]['bar_trend_3_hr']),
            pressure_last=inhg_to_mmhg(message['sensors'][2]['data'][0]['pressure_last'])
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
            bar=inhg_to_mmhg(message['sensors'][0]['data'][0]['bar']),
            bar_absolute=inhg_to_mmhg(message['sensors'][0]['data'][0]['bar_absolute']),
            bar_trend=inhg_to_mmhg(message['sensors'][0]['data'][0]['bar_trend'], to_round=True),
            dew_point=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['dew_point']),
            et_day=in_to_mm(message['sensors'][0]['data'][0]['et_day']),
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

def consume_historic_msg(message)->DavisMessage:
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
            bar_trend_3_hr=inhg_to_mmhg(message['sensors'][2]['data'][0]['bar_trend_3_hr']),
            pressure_last=inhg_to_mmhg(message['sensors'][2]['data'][0]['pressure_last'])
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
            data_structure_type=6,
            ts=message['sensors'][0]['data'][0]['ts'],
            tz_offset=message.get('sensors', [{}])[0].get('data', [{}])[0].get('tz_offset', 3600),
            bar=inhg_to_mmhg(message['sensors'][0]['data'][0]['bar']),
            bar_absolute=inhg_to_mmhg(message['sensors'][0]['data'][0]['abs_press']),
            bar_trend=None,
            dew_point=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['dew_point_out'], to_round=True),
            et_day=in_to_mm(message['sensors'][0]['data'][0]['et']),
            forecast_rule=None,
            forecast_desc=None,
            heat_index=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['heat_index_out'], to_round=True),
            hum_out=message['sensors'][0]['data'][0]['hum_out'],

            rain_15_min_clicks=message['sensors'][0]['data'][0]['rainfall_clicks'],
            rain_15_min_in=message['sensors'][0]['data'][0]['rainfall_in'],
            rain_15_min_mm=message['sensors'][0]['data'][0]['rainfall_mm'],
            rain_60_min_clicks=None,
            rain_60_min_in=None,
            rain_60_min_mm=None,
            rain_24_hr_clicks=None,
            rain_24_hr_in=None,
            rain_24_hr_mm=None,
            rain_day_clicks=None,
            rain_day_in=None,
            rain_day_mm=None,

            # DONE
            rain_rate_clicks=message['sensors'][0]['data'][0]['rain_rate_hi_clicks'],
            rain_rate_in=message['sensors'][0]['data'][0]['rain_rate_hi_in'],
            rain_rate_mm=message['sensors'][0]['data'][0]['rain_rate_hi_mm'],
            # DONE
            rain_storm_clicks=None,
            rain_storm_in=None,
            rain_storm_mm=None,
            rain_storm_start_date=None,
            solar_rad=message['sensors'][0]['data'][0]['solar_rad_avg'],
            temp_out=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['temp_out']),
            thsw_index=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['thsw_index']),
            uv=message['sensors'][0]['data'][0]['uv_index_avg'],
            wind_chill=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['wind_chill'], to_round=True),
            wind_dir=integer_to_angle(message['sensors'][0]['data'][0]['wind_dir_of_hi']),
            wind_dir_of_gust_10_min=None,
            wind_gust_10_min=None,
            wind_speed=mph_to_kmh(message['sensors'][0]['data'][0]['wind_speed_avg']),
            wind_speed_2_min=None,
            wind_speed_10_min=None,
            wet_bulb=fahrenheit_to_celsius(message['sensors'][0]['data'][0]['wet_bulb'])
        )
    )
    return davis_message

def inhg_to_mmhg(pressure_in: Optional[float], to_round: bool = False) -> Optional[float]:
    """
    Get pressure in inch - Hg and turn into mm - Hg
    1 mmHg = 133.322 pascals (Pa)
    1 inHg = 3386.39 pascals (Pa)
    mmHg value x 133.322 Pa = inHg value x 3386.39 Pa
    mmHg value = inHg value x 25.4

    :param to_round:
    :param pressure_in:
    :return:
    """
    if pressure_in:
        if to_round:
            return round(float(pressure_in * 25.4))
        else:
            return float(pressure_in * 25.4)
    else:
        return None

def fahrenheit_to_celsius(temperature_f: Optional[Union[float, int]], to_round: bool = False) -> Optional[Union[float, int]]:
    """
    Get temperature in Fahrenheit (°F) and
    convert to Celsius (°C)
    °C = (°F - 32) ÷ (9/5) or °C = (°F - 32) ÷ (1.8)

    :param to_round:
    :param temperature_f:
    :return:
    """
    if temperature_f is None:
        return None
    elif to_round:
        return round((temperature_f * units.degF).to(units.degC).magnitude)
    elif type(temperature_f) is float:
        return float((temperature_f * units.degF).to(units.degC).magnitude)
    elif type(temperature_f) is int:
        return round((temperature_f * units.degF).to(units.degC).magnitude)

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
    if wind_dir_d is None:
        return None

def integer_to_angle(wind_dir: Optional[int]) -> Optional[int]:
    """
    Converts wind direction in WeatherLink format to regular angle value.

    :param wind_dir:
    :return:
    """
    if wind_dir is None:
        return None
    else:
        direction_codes = {
            0: "N",  # North
            1: "NNE",  # North-Northeast
            2: "NE",  # Northeast
            3: "ENE",  # East-Northeast
            4: "E",  # East
            5: "ESE",  # East-Southeast
            6: "SE",  # Southeast
            7: "SSE",  # South-Southeast
            8: "S",  # South
            9: "SSW",  # South-Southwest
            10: "SW",  # Southwest
            11: "WSW",  # West-Southwest
            12: "W",  # West
            13: "WNW",  # West-Northwest
            14: "NW",  # Northwest
            15: "NNW"  # North-Northwest
        }
        return direction_to_angle(direction_codes[wind_dir])


def mph_to_kmh(mph_val: Optional[int]) -> Optional[int]:
    """
    Convert mph (miles per hour) to km/h (kilometers per hour)
    1 mile per hour = 1.609344 kilometers per hour

    :param mph_val:
    :return:
    """
    if mph_val:
        return round((mph_val * units.mph).to(units.km / units.hour).magnitude)
    else:
        return None

def in_to_mm(in_val: Optional[float]) -> Optional[float]:
    """
    Convert inch to mm.

    :param in_val:
    :return:
    """
    if in_val:
        return (in_val * units.inch).to(units.mm).magnitude
    else:
        return None
