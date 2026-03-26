from fastapi import APIRouter

router = APIRouter(prefix="/api/scrape", tags=["scrape"])


@router.post("")
async def trigger_scrape():
    return {"message": "Scrape endpoint — coming in feature/otodom-scraper"}


@router.get("/status")
async def scrape_status():
    return {"message": "Scrape status — coming in feature/otodom-scraper"}
