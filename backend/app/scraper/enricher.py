import asyncio
import json
import logging
import random
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Listing
from app.scraper.otodom import (
    USER_AGENTS, METRO_STATIONS, CENTER_POINT,
    walking_minutes, transit_minutes,
)

logger = logging.getLogger(__name__)

BATCH_SIZE = 50
FEATURES_MAP = {
    "wanna": "has_bathtub",
    "balkon": "has_balcony",
    "ogród": "has_garden",
    "ogródek": "has_garden",
    "garaż": "has_parking",
    "miejsce parkingowe": "has_parking",
    "winda": "has_elevator",
}

PETS_KEYWORDS = ["zwierzęta", "przyjazne zwierzętom", "pets"]


async def enrich_listing(client: httpx.AsyncClient, listing: Listing, db: Session) -> bool:
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        resp = await client.get(listing.url, headers=headers, follow_redirects=True)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        script = soup.find("script", {"id": "__NEXT_DATA__"})
        if not script:
            return False

        data = json.loads(script.string)
        ad = data.get("props", {}).get("pageProps", {}).get("ad", {})
        if not ad:
            return False

        # Features
        features = [f.lower() for f in ad.get("features", []) if isinstance(f, str)]
        description = (ad.get("description") or "").lower()
        all_text = features + [description]

        listing.has_bathtub = any("wanna" in t for t in all_text)
        listing.has_balcony = any("balkon" in f for f in features)
        listing.has_garden = any(k in f for f in features for k in ["ogród", "ogródek"])
        listing.has_parking = any(k in f for f in features for k in ["garaż", "parking", "miejsce parkingowe"])
        listing.has_elevator = any("winda" in f for f in features)
        listing.pets_allowed = any(
            k in t for t in all_text for k in ["zwierzęta", "zwierzęt", "zwierzat", "pet friendly", "pets"]
        )

        # Furnished
        if any("meble" in f for f in features):
            listing.furnished = "yes"

        # Characteristics
        for char in ad.get("characteristics", []):
            key = char.get("key", "")
            val = char.get("value", "")
            if key == "deposit" and val:
                try:
                    listing.deposit = float(val)
                except (ValueError, TypeError):
                    pass
            elif key == "heating" and val:
                listing.heating = val
            elif key == "building_floors_num" and val:
                try:
                    listing.total_floors = int(val)
                except (ValueError, TypeError):
                    pass
            elif key == "free_from" and val:
                try:
                    from datetime import date as date_type
                    listing.available_from = date_type.fromisoformat(val)
                except (ValueError, TypeError):
                    pass

        # Description
        listing.description = ad.get("description", listing.description)

        # Coordinates
        coords = ad.get("location", {}).get("coordinates", {})
        lat = coords.get("latitude")
        lon = coords.get("longitude")
        if lat and lon:
            listing.latitude = lat
            listing.longitude = lon
            listing.metro_distance_min = walking_minutes(lat, lon, METRO_STATIONS)
            listing.center_distance_min = transit_minutes(lat, lon, CENTER_POINT)

        listing.last_updated = datetime.utcnow()
        db.commit()
        return True

    except Exception as e:
        logger.warning("Failed to enrich listing %s: %s", listing.otodom_id, e)
        return False


async def enrich_batch():
    db = SessionLocal()
    try:
        listings = (
            db.query(Listing)
            .filter(Listing.is_active == True, Listing.latitude.is_(None))  # noqa: E712
            .limit(BATCH_SIZE)
            .all()
        )

        if not listings:
            logger.info("No listings to enrich")
            return 0

        logger.info("Enriching %d listings...", len(listings))
        enriched = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            for listing in listings:
                ok = await enrich_listing(client, listing, db)
                if ok:
                    enriched += 1
                await asyncio.sleep(random.uniform(1.0, 2.5))

        logger.info("Enriched %d/%d listings", enriched, len(listings))
        return enriched
    finally:
        db.close()
