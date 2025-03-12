import traceback

from sqlalchemy.ext.asyncio import AsyncSession

from app.davis.schemas import DavisMessage
from app.logs.config_server_logs import server_logger
import app.crud.davis_sensors as db_service


async def process_davis_message(db: AsyncSession, message: DavisMessage):
    server_logger.info(f"DAVIS -- Received message: {message}")

    resp = await db_service.create_davis_sensors(db, message)

    if resp is None:
        try:
            server_logger.info(f"DAVIS -- Station data already inserted for ts : {message.vantagePro_msg.ts}")
        except Exception as e:
            server_logger.error("".join(traceback.format_exception(None, e, e.__traceback__)))
            server_logger.error(f"Error during Davis scheduled task: {e}")
    else:
        response = {"status": "success", "message": "Davis reading created.", "details": f"{resp.__dict__}"}
        server_logger.info(response)
    return message


