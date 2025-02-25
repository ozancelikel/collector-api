from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.campbell.service import run_campbell_scraper
from app.logs.config_server_logs import server_logger
from app.config import settings

# Use AsyncIOScheduler for async jobs
scheduler = AsyncIOScheduler()

async def scheduled_task():
    """Runs the scraper on a schedule."""
    print("Running scheduled scraping task...")
    data = await run_campbell_scraper(hourly=settings.SCRAPER_HOURLY)
    server_logger.info(f"Task done :  {data}")

def start_scheduler():
    """Start the scheduler and add jobs."""
    if not scheduler.running:
        scheduler.add_job(scheduled_task, "interval", minutes=settings.SCRAPER_FREQ)
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
