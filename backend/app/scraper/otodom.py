import asyncio
import json
import math
import random
import logging
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Listing, PriceHistory, ScrapeRun
from app.config import SCRAPE_INTERVAL_HOURS

logger = logging.getLogger(__name__)

SEARCH_URLS = [
    "https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/mazowieckie/warszawa/warszawa/warszawa",
]

QUERY_PARAMS = {
    "limit": 72,
    "ownerTypeSingleSelect": "ALL",
    "by": "LATEST",
    "direction": "DESC",
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
]

# Warsaw metro stations (M1 + M2)
METRO_STATIONS = [
    (52.1983, 20.9840, "Kabaty"),
    (52.2019, 20.9857, "Natolin"),
    (52.2084, 20.9893, "Imielin"),
    (52.2115, 20.9822, "Stokłosy"),
    (52.2155, 20.9825, "Ursynów"),
    (52.2167, 20.9892, "Służew"),
    (52.2193, 20.9954, "Wilanowska"),
    (52.2239, 21.0027, "Wierzbno"),
    (52.2275, 21.0037, "Racławicka"),
    (52.2294, 21.0039, "Pole Mokotowskie"),
    (52.2289, 21.0101, "Politechnika"),
    (52.2297, 21.0122, "Centrum"),
    (52.2319, 21.0067, "Świętokrzyska"),
    (52.2354, 21.0031, "Ratusz Arsenał"),
    (52.2415, 20.9974, "Dworzec Gdański"),
    (52.2457, 20.9926, "Plac Wilsona"),
    (52.2523, 20.9850, "Marymont"),
    (52.2546, 20.9744, "Słodowiec"),
    (52.2592, 20.9637, "Stare Bielany"),
    (52.2637, 20.9515, "Wawrzyszew"),
    (52.2691, 20.9380, "Młociny"),
    # M2
    (52.2321, 20.9204, "Bemowo"),
    (52.2372, 20.9334, "Ulrychów"),
    (52.2381, 20.9479, "Księcia Janusza"),
    (52.2380, 20.9599, "Młynów"),
    (52.2344, 20.9768, "Płocka"),
    (52.2327, 20.9868, "Rondo Daszyńskiego"),
    (52.2316, 20.9968, "Rondo ONZ"),
    (52.2319, 21.0067, "Świętokrzyska"),
    (52.2313, 21.0165, "Nowy Świat-Uniwersytet"),
    (52.2285, 21.0289, "Centrum Nauki Kopernik"),
    (52.2278, 21.0442, "Stadion Narodowy"),
    (52.2458, 21.0444, "Dworzec Wileński"),
    (52.2508, 21.0519, "Szwedzka"),
    (52.2565, 21.0602, "Targówek Mieszkaniowy"),
    (52.2612, 21.0690, "Trocka"),
    (52.2854, 21.0649, "Zacisze"),
    (52.2924, 21.0548, "Kondratowicza"),
    (52.2977, 21.0457, "Bródno"),
]

CENTER_POINT = (52.2297, 21.0122)  # Centrum / Palac Kultury
WALKING_SPEED_KMH = 5.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def distance_to_min(lat: float, lon: float, points: list[tuple]) -> int:
    min_km = min(haversine_km(lat, lon, p[0], p[1]) for p in points)
    return round((min_km / WALKING_SPEED_KMH) * 60)


ROOMS_MAP = {
    "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5,
    "SIX": 6, "SEVEN": 7, "EIGHT": 8, "NINE": 9, "TEN": 10,
}

FLOOR_MAP = {
    "GROUND": 0, "FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4,
    "FIFTH": 5, "SIXTH": 6, "SEVENTH": 7, "EIGHTH": 8, "NINTH": 9,
    "TENTH": 10, "ELEVENTH": 11, "TWELFTH": 12, "THIRTEENTH": 13,
    "FOURTEENTH": 14, "FIFTEENTH": 15, "HIGHER_THAN_15": 16,
    "GARRET": -1, "CELLAR": -2,
}


def parse_listing_from_item(item: dict) -> dict:
    otodom_id = str(item.get("id", ""))
    slug = item.get("slug", "")
    url = f"https://www.otodom.pl/pl/oferta/{slug}" if slug else ""
    title = item.get("title", "")

    # Price
    price = None
    total_price = item.get("totalPrice")
    if total_price and isinstance(total_price, dict):
        price = total_price.get("value")
    if price is None:
        rent_price = item.get("rentPrice")
        if rent_price and isinstance(rent_price, dict):
            price = rent_price.get("value")

    deposit = None
    deposit_data = item.get("deposit")
    if deposit_data and isinstance(deposit_data, dict):
        deposit = deposit_data.get("value")

    agency_fee = item.get("agency") is not None

    # Location — extract district from reverseGeocoding
    location = item.get("location", {})
    address_obj = location.get("address", {})

    district = None
    address = None
    reverse_geo = location.get("reverseGeocoding", {})
    for loc in reverse_geo.get("locations", []):
        if loc.get("locationLevel") == "district":
            district = loc.get("name")
        elif loc.get("locationLevel") == "residential":
            address = loc.get("fullName")

    if not address:
        street = address_obj.get("street", {})
        street_name = street.get("name", "") if isinstance(street, dict) else ""
        street_num = street.get("number", "") if isinstance(street, dict) else ""
        if street_name:
            address = f"{street_name} {street_num}".strip()

    # Coordinates — not always available in list view
    map_details = location.get("mapDetails", {})
    latitude = map_details.get("latitude") if isinstance(map_details, dict) else None
    longitude = map_details.get("longitude") if isinstance(map_details, dict) else None

    # Area — direct field
    area = item.get("areaInSquareMeters")
    if area is not None:
        try:
            area = float(area)
        except (ValueError, TypeError):
            area = None

    # Rooms — string like "TWO"
    rooms_str = item.get("roomsNumber", "")
    rooms = ROOMS_MAP.get(rooms_str)

    # Floor — string like "FIFTH"
    floor_str = item.get("floorNumber", "")
    floor = FLOOR_MAP.get(floor_str) if floor_str else None
    total_floors = None  # not available in list view

    # Features — not available in list view, set defaults
    has_balcony = False
    has_garden = False
    has_parking = False
    has_elevator = False
    pets_allowed = None
    has_bathtub = None

    # Also try legacy characteristics/features if present
    for char in item.get("characteristics", []):
        key = char.get("key", "")
        val = char.get("value", "")
        if key == "rooms_num" and rooms is None:
            try:
                rooms = int(val)
            except (ValueError, TypeError):
                pass
        elif key == "m" and area is None:
            try:
                area = float(val)
            except (ValueError, TypeError):
                pass

    features = [f.upper() if isinstance(f, str) else "" for f in item.get("features", [])]
    if features:
        has_balcony = "BALCONY" in features
        has_garden = "GARDEN" in features
        has_parking = "GARAGE" in features or "PARKING" in features
        has_elevator = "ELEVATOR" in features
        pets_allowed = True if "PETS_FRIENDLY" in features else None
        has_bathtub = True if "BATHTUB" in features else None

    # Images — use "large" or "medium" field
    images_list = []
    for img in item.get("images", []):
        if isinstance(img, dict):
            img_url = img.get("large") or img.get("medium") or img.get("url", "")
            if img_url:
                images_list.append(img_url)
    images_json = json.dumps(images_list) if images_list else None

    # Metro/center distance
    metro_distance_min = None
    center_distance_min = None
    if latitude and longitude:
        metro_distance_min = distance_to_min(latitude, longitude, METRO_STATIONS)
        center_distance_min = distance_to_min(latitude, longitude, [CENTER_POINT])

    return {
        "otodom_id": otodom_id,
        "url": url,
        "title": title,
        "price": price,
        "deposit": deposit,
        "agency_fee": agency_fee,
        "rooms": rooms,
        "area": area,
        "floor": floor,
        "total_floors": total_floors,
        "district": district,
        "address": address,
        "has_balcony": has_balcony,
        "has_garden": has_garden,
        "has_parking": has_parking,
        "has_elevator": has_elevator,
        "pets_allowed": pets_allowed,
        "has_bathtub": has_bathtub,
        "latitude": latitude,
        "longitude": longitude,
        "images": images_json,
        "metro_distance_min": metro_distance_min,
        "center_distance_min": center_distance_min,
    }


MAX_PAGES = 5  # Limit pages per scrape to avoid long runs (5 * 72 = 360 listings)


async def fetch_page(client: httpx.AsyncClient, url: str, page: int) -> tuple[list[dict], int]:
    """Returns (items, total_pages)."""
    params = {**QUERY_PARAMS, "page": page}
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    resp = await client.get(url, params=params, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    script = soup.find("script", {"id": "__NEXT_DATA__"})
    if not script:
        logger.warning("No __NEXT_DATA__ found on page %d", page)
        return [], 0

    data = json.loads(script.string)
    search_ads = (
        data.get("props", {})
        .get("pageProps", {})
        .get("data", {})
        .get("searchAds", {})
    )
    items = search_ads.get("items", [])
    total_pages = search_ads.get("pagination", {}).get("totalPages", 1)
    return items, total_pages


def save_listings(db: Session, parsed: list[dict], run: ScrapeRun) -> list[int]:
    new_ids = []
    now = datetime.utcnow()

    for data in parsed:
        existing = db.query(Listing).filter(Listing.otodom_id == data["otodom_id"]).first()

        if existing is None:
            listing = Listing(**data, first_seen=now, last_seen=now, last_updated=now)
            db.add(listing)
            db.flush()
            new_ids.append(listing.id)
            run.listings_new += 1
        else:
            existing.last_seen = now
            if existing.price != data.get("price") and data.get("price") is not None:
                db.add(PriceHistory(
                    listing_id=existing.id,
                    price=data["price"],
                    recorded_at=now,
                ))
                existing.price = data["price"]
                existing.last_updated = now
                run.listings_updated += 1
            existing.is_active = True

    db.commit()
    return new_ids


async def run_scrape() -> int:
    db = SessionLocal()
    run = ScrapeRun(started_at=datetime.utcnow())
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        all_parsed = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for base_url in SEARCH_URLS:
                page = 1
                while page <= MAX_PAGES:
                    logger.info("Scraping page %d of %s", page, base_url)
                    items, total_pages = await fetch_page(client, base_url, page)
                    if not items:
                        break

                    for item in items:
                        parsed = parse_listing_from_item(item)
                        if parsed["otodom_id"]:
                            all_parsed.append(parsed)

                    run.listings_found += len(items)
                    logger.info("Page %d: got %d items (total pages: %d)", page, len(items), total_pages)

                    if page >= min(total_pages, MAX_PAGES):
                        break

                    page += 1
                    await asyncio.sleep(random.uniform(1.5, 3.5))

        new_ids = save_listings(db, all_parsed, run)
        run.finished_at = datetime.utcnow()
        db.commit()

        if new_ids:
            from app.notifications.alerts import check_and_notify
            await check_and_notify(db, new_ids)

        logger.info(
            "Scrape done: found=%d, new=%d, updated=%d",
            run.listings_found, run.listings_new, run.listings_updated,
        )
        return run.id

    except Exception as e:
        run.error = str(e)
        run.finished_at = datetime.utcnow()
        db.commit()
        logger.exception("Scrape failed")
        raise
    finally:
        db.close()
