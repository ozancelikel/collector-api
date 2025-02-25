from fastapi import APIRouter
from app.campbell.service import run_campbell_scraper
from app.config import settings

router = APIRouter()

@router.get("/scrape")
async def scrape_data():
    """Manually triggers the scraper."""
    # TODO: Make this endpoint secure!
    data = await run_campbell_scraper(hourly=settings.SCRAPER_HOURLY)
    return {"status": "success", "data": data}