import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ScrapeRun
from app.schemas import ScrapeRunOut
from app.scraper.otodom import run_scrape
from app.scraper.enricher import enrich_batch

router = APIRouter(prefix="/api/scrape", tags=["scrape"])


@router.post("")
async def trigger_scrape():
    asyncio.create_task(run_scrape())
    return {"status": "started"}


@router.post("/enrich")
async def trigger_enrich():
    asyncio.create_task(enrich_batch())
    return {"status": "enrichment started"}


@router.get("/status", response_model=list[ScrapeRunOut])
async def scrape_status(db: Session = Depends(get_db)):
    runs = db.query(ScrapeRun).order_by(ScrapeRun.started_at.desc()).limit(10).all()
    return runs
