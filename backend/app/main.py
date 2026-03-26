import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import init_db
from app.config import SCRAPE_INTERVAL_HOURS
from app.routers import listings, scrape
from app.scraper.otodom import run_scrape
from app.scraper.enricher import enrich_batch

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Otodom Scraper API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(listings.router)
app.include_router(scrape.router)

scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup():
    init_db()
    scheduler.add_job(run_scrape, "interval", hours=SCRAPE_INTERVAL_HOURS)
    scheduler.add_job(enrich_batch, "interval", minutes=10)
    scheduler.start()


@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()


@app.get("/api/health")
async def health():
    return {"status": "ok"}
