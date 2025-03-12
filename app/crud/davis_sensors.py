import traceback
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.davis.schemas import DavisMessage
from app.models.models import DavisStation, DavisBarometer, DavisVantagePro2, DavisGatewayQuectel
from app.logs.config_server_logs import server_logger as logger


async def create_davis_sensors(db: AsyncSession, message: DavisMessage) -> Optional[DavisStation]:
    barometer_id = uuid.uuid4()
    gateway_id = uuid.uuid4()
    vantage_id = uuid.uuid4()

    if await check_existing_ts(db, message):
        new_vantagePro = DavisVantagePro2(
            id=vantage_id,
            lsid=message.vantagePro_msg.lsid,
            ts=message.vantagePro_msg.ts,
            tz_offset=message.vantagePro_msg.tz_offset,
            date=datetime.fromtimestamp(message.vantagePro_msg.ts),
            sensor_data_structure_id=f"{message.vantagePro_msg.sensor_type}_{message.vantagePro_msg.data_structure_type}",
            bar=message.vantagePro_msg.bar,
            bar_absolute=message.vantagePro_msg.bar_absolute,
            bar_trend=message.vantagePro_msg.bar_trend,
            dew_point=message.vantagePro_msg.dew_point,
            et_day=message.vantagePro_msg.et_day,
            forecast_rule=message.vantagePro_msg.forecast_rule,
            forecast_desc=message.vantagePro_msg.forecast_desc,
            heat_index=message.vantagePro_msg.heat_index,
            hum_out=message.vantagePro_msg.hum_out,
            rain_15_min_clicks=message.vantagePro_msg.rain_15_min_clicks,
            rain_15_min_in=message.vantagePro_msg.rain_15_min_in,
            rain_15_min_mm=message.vantagePro_msg.rain_15_min_mm,
            rain_60_min_clicks=message.vantagePro_msg.rain_60_min_clicks,
            rain_60_min_in=message.vantagePro_msg.rain_60_min_in,
            rain_60_min_mm=message.vantagePro_msg.rain_60_min_mm,
            rain_24_hr_clicks=message.vantagePro_msg.rain_24_hr_clicks,
            rain_24_hr_in=message.vantagePro_msg.rain_24_hr_in,
            rain_24_hr_mm=message.vantagePro_msg.rain_24_hr_mm,
            rain_day_clicks=message.vantagePro_msg.rain_day_clicks,
            rain_day_in=message.vantagePro_msg.rain_day_in,
            rain_day_mm=message.vantagePro_msg.rain_day_mm,
            rain_rate_clicks=message.vantagePro_msg.rain_rate_clicks,
            rain_rate_in=message.vantagePro_msg.rain_rate_in,
            rain_rate_mm=message.vantagePro_msg.rain_rate_mm,
            rain_storm_clicks=message.vantagePro_msg.rain_storm_clicks,
            rain_storm_in=message.vantagePro_msg.rain_storm_in,
            rain_storm_mm=message.vantagePro_msg.rain_storm_mm,
            rain_storm_start_date=message.vantagePro_msg.rain_storm_start_date,
            solar_rad=message.vantagePro_msg.solar_rad,
            temp_out=message.vantagePro_msg.temp_out,
            thsw_index=message.vantagePro_msg.thsw_index,
            uv=message.vantagePro_msg.uv,
            wind_chill=message.vantagePro_msg.wind_chill,
            wind_dir=message.vantagePro_msg.wind_dir,
            wind_dir_of_gust_10_min=message.vantagePro_msg.wind_dir_of_gust_10_min,
            wind_gust_10_min=message.vantagePro_msg.wind_gust_10_min,
            wind_speed=message.vantagePro_msg.wind_speed,
            wind_speed_2_min=message.vantagePro_msg.wind_speed_2_min,
            wind_speed_10_min=message.vantagePro_msg.wind_speed_10_min,
            wet_bulb=message.vantagePro_msg.wet_bulb
        )

        new_gateway = DavisGatewayQuectel(
            id=gateway_id,
            lsid=message.gateway_msg.lsid,
            ts=message.gateway_msg.ts,
            tz_offset=message.gateway_msg.tz_offset,
            date=datetime.fromtimestamp(message.gateway_msg.ts),
            sensor_data_structure_id=f"{message.gateway_msg.sensor_type}_{message.gateway_msg.data_structure_type}",
            iss_solar_panel_voltage=message.gateway_msg.iss_solar_panel_voltage,
            last_gps_reading_timestamp=message.gateway_msg.last_gps_reading_timestamp,
            resyncs=message.gateway_msg.resyncs,
            transmitter_battery_state=message.gateway_msg.transmitter_battery_state,
            crc_errors=message.gateway_msg.crc_errors,
            tiva_application_firmware_version=message.gateway_msg.tiva_application_firmware_version,
            lead_acid_battery_voltage=message.gateway_msg.lead_acid_battery_voltage,
            iss_transmitter_battery_voltage=message.gateway_msg.iss_transmitter_battery_voltage,
            beacon_interval=message.gateway_msg.beacon_interval,
            davistalk_rssi=message.gateway_msg.davistalk_rssi,
            solar_panel_voltage=message.gateway_msg.solar_panel_voltage,
            rank=message.gateway_msg.rank,
            false_wakeup_rssi=message.gateway_msg.false_wakeup_rssi,
            cell_id=message.gateway_msg.cell_id,
            longitude=message.gateway_msg.longitude,
            power_percentage_mcu=message.gateway_msg.power_percentage_mcu,
            mcc_mnc=message.gateway_msg.mcc_mnc,
            iss_super_cap_voltage=message.gateway_msg.iss_super_cap_voltage,
            false_wakeup_count=message.gateway_msg.false_wakeup_count,
            etx=message.gateway_msg.etx,
            number_of_neighbors=message.gateway_msg.number_of_neighbors,
            last_parent_rtt_ping=message.gateway_msg.last_parent_rtt_ping,
            bootloader_version=message.gateway_msg.bootloader_version,
            cme=message.gateway_msg.cme,
            cc1310_firmware_version=message.gateway_msg.cc1310_firmware_version,
            power_percentage_rx=message.gateway_msg.power_percentage_rx,
            good_packet_streak=message.gateway_msg.good_packet_streak,
            rpl_parent_node_id=message.gateway_msg.rpl_parent_node_id,
            afc_setting=message.gateway_msg.afc_setting,
            overall_access_technology=message.gateway_msg.overall_access_technology,
            cell_channel=message.gateway_msg.cell_channel,
            noise_floor_rssi=message.gateway_msg.noise_floor_rssi,
            latitude=message.gateway_msg.latitude,
            cereg=message.gateway_msg.cereg,
            last_cme_error_timestamp=message.gateway_msg.last_cme_error_timestamp,
            bluetooth_firmware_version=message.gateway_msg.bluetooth_firmware_version,
            location_area_code=message.gateway_msg.location_area_code,
            link_layer_packets_received=message.gateway_msg.link_layer_packets_received,
            reception_percent=message.gateway_msg.reception_percent,
            rx_bytes=message.gateway_msg.rx_bytes,
            link_uptime=message.gateway_msg.link_uptime,
            creg_cgreg=message.gateway_msg.creg_cgreg,
            health_version=message.gateway_msg.health_version,
            inside_box_temp=message.gateway_msg.inside_box_temp,
            tx_bytes=message.gateway_msg.tx_bytes,
            elevation=message.gateway_msg.elevation,
            power_percentage_tx=message.gateway_msg.power_percentage_tx,
            rssi=message.gateway_msg.rssi,
            last_rx_rssi=message.gateway_msg.last_rx_rssi,
            rpl_mode=message.gateway_msg.rpl_mode,
            uptime=message.gateway_msg.uptime,
            platform_id=message.gateway_msg.platform_id
        )

        new_barometer = DavisBarometer(
            id=barometer_id,
            lsid=message.barometer_msg.lsid,
            ts=message.barometer_msg.ts,
            tz_offset=message.barometer_msg.tz_offset,
            date=datetime.fromtimestamp(message.barometer_msg.ts),
            sensor_data_structure_id=f"{message.barometer_msg.sensor_type}_{message.barometer_msg.data_structure_type}",
            pressure_last=message.barometer_msg.pressure_last,
            bar_trend_3_hr=message.barometer_msg.bar_trend_3_hr
        )

        new_station = DavisStation(
            station_id=message.station_id,
            station_id_uuid=message.station_id_uuid,

            barometer_reading=barometer_id,
            gatewayquectel_reading=gateway_id,
            vantagepro2_reading=vantage_id,
        )

        db.add(new_vantagePro)
        db.add(new_gateway)
        db.add(new_barometer)
        try:
            await db.commit()
            await db.refresh(new_vantagePro)
            await db.refresh(new_gateway)
            await db.refresh(new_barometer)
        except Exception as e:
            logger.error(e)
            raise e
        try:
            db.add(new_station)
            await db.commit()
        except Exception as e:
            logger.error("".join(traceback.format_exception(None, e, e.__traceback__)))
            logger.error(f"Error during Davis scheduled task: {e}")
            raise e

        await db.refresh(new_station)

        return new_station
    else:
        return None


async def check_existing_ts(db: AsyncSession, message: DavisMessage):
    result = await db.execute(select(DavisVantagePro2).filter(DavisVantagePro2.ts == message.vantagePro_msg.ts))
    existing_entry = result.scalars().first()

    if existing_entry:
        print("Record with the same timestamp already exists. Skipping insertion.")
        return False
    else:
        return True