import traceback

import httpx
from fastapi import APIRouter, HTTPException, Depends, Header
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


@router.get("/receive_message/")
async def receive_message(api_key: str = Depends(api_key_dependency), db: AsyncSession = Depends(get_db)):

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
            message: DavisMessage = consume_message(response_data)
            server_logger.info(f"Received message with station_id: {message.station_id} and UUID: {message.station_id_uuid}")
        except Exception as e:
            server_logger.error(f"ERROR CODE 500 - Error parsing Davis response: {str(e)}")
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
            pressure_last=message['sensors'][2]['data'][0]['pressure_last']
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
            inside_box_temp=message['sensors'][1]['data'][0]['inside_box_temp'],
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
            bar=message['sensors'][0]['data'][0]['bar'],
            bar_absolute=message['sensors'][0]['data'][0]['bar_absolute'],
            bar_trend=message['sensors'][0]['data'][0]['bar_trend'],
            dew_point=message['sensors'][0]['data'][0]['dew_point'],
            et_day=message['sensors'][0]['data'][0]['et_day'],
            forecast_rule=message['sensors'][0]['data'][0]['forecast_rule'],
            forecast_desc=message['sensors'][0]['data'][0]['forecast_desc'],
            heat_index=message['sensors'][0]['data'][0]['heat_index'],
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
            temp_out=message['sensors'][0]['data'][0]['temp_out'],
            thsw_index=message['sensors'][0]['data'][0]['thsw_index'],
            uv=message['sensors'][0]['data'][0]['uv'],
            wind_chill=message['sensors'][0]['data'][0]['wind_chill'],
            wind_dir=message['sensors'][0]['data'][0]['wind_dir'],
            wind_dir_of_gust_10_min=message['sensors'][0]['data'][0]['wind_dir_of_gust_10_min'],
            wind_gust_10_min=message['sensors'][0]['data'][0]['wind_gust_10_min'],
            wind_speed=message['sensors'][0]['data'][0]['wind_speed'],
            wind_speed_2_min=message['sensors'][0]['data'][0]['wind_speed_2_min'],
            wind_speed_10_min=message['sensors'][0]['data'][0]['wind_speed_10_min'],
            wet_bulb=message['sensors'][0]['data'][0]['wet_bulb']
        )
    )
    return davis_message

