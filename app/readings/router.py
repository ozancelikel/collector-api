import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.readings.schemas import HelixMessage, WindMessage
import app.readings.service as reading_service
from app.db.session import get_db

router = APIRouter()


@router.post("/helix")
async def receive_helix_message_temp(message: HelixMessage, db: AsyncSession = Depends(get_db)):
    try:
        db_resp = await reading_service.process_helix_message(db, message)
        return db_resp
    except Exception as e:
        logging.error(f"ERROR CODE 500 - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wind")
async def receive_wind_message(message: WindMessage, db: AsyncSession = Depends(get_db)):
    try:
        resp: dict = await reading_service.process_wind_message(db, message)
        return resp
    except Exception as e:
        logging.error(f"ERROR CODE 500 - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sensors/{serial_number}")
async def get_sensor_by_serial_number(serial_number: str, db: AsyncSession = Depends(get_db)):
    try:
        db_resp = await reading_service.process_get_sensor_by_serial_number(db, serial_number)
        return db_resp
    except Exception as e:
        logging.error(f"ERROR CODE 500 - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
