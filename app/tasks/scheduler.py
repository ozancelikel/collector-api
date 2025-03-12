import traceback

import httpx
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.campbell.service import run_campbell_scraper
from app.logs.config_server_logs import server_logger
from app.config import settings

# Use AsyncIOScheduler for async jobs
scheduler = AsyncIOScheduler()

async def scheduled_scraping_task():
    """Runs the scraper on a schedule."""
    print("Running scheduled scraping task...")
    data = await run_campbell_scraper(hourly=settings.SCRAPER_HOURLY)
    server_logger.info(f"Task done :  {data}")


async def call_davis_route():
    async with httpx.AsyncClient() as client:
        headers = {
            'x-api-key': settings.DAVIS_INTERNAL_API_KEY
        }
        try:
            response = await client.get("http://localhost:8000/davis/receive_message/", headers=headers)
            if response.status_code == 200:
                server_logger.info("Successfully sent message to external API")
            else:
                server_logger.error(f"Failed to send message, status code: {response.status_code}")
                server_logger.error(f"Response body: {response.text}")  # Logs the error response body
        except Exception as e:
                server_logger.error("An error occurred during the scheduled task:")
                server_logger.error("".join(traceback.format_exception(None, e, e.__traceback__)))
                server_logger.error(f"Error during Davis scheduled task: {e}")

def start_scheduler():
    """Start the scheduler and add jobs."""
    if not scheduler.running:
        scheduler.add_job(scheduled_scraping_task, "interval", minutes=settings.SCRAPER_FREQ)
        server_logger.info("Campbell scraper task added to scheduler.")
        scheduler.add_job(call_davis_route, "interval", minutes=settings.DAVIS_TRIGGER_FREQ)
        server_logger.info("Davis route task added to scheduler.")
        # For debugging:
        # scheduler.add_job(scheduled_task, 'date', id='one_time_job', run_date=None)

        scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        scheduler.start()
        server_logger.info("Async Scheduler started.")

def job_listener(event):
    """Listener to track job execution status."""
    if event.exception:
        server_logger.error(f"Job {event.job_id} failed with exception: {event.exception}")
    else:
        server_logger.info(f"Job {event.job_id} completed successfully")
        server_logger.info(f"Job {event.job_id} ran at {event.scheduled_run_time}")

def shutdown_scheduler():
    """Gracefully shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        server_logger.info("Async Scheduler stopped.")
    else:
        server_logger.info("Scheduler was not running.")
