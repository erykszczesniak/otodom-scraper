import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session
from app.models import Listing
from app.notifications.email import send_email_alert
from app.notifications.telegram import send_telegram_alert

logger = logging.getLogger(__name__)

ALERTS_PATH = Path("data/alerts.json")


def load_alerts() -> list[dict]:
    if not ALERTS_PATH.exists():
        return []
    try:
        return json.loads(ALERTS_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error("Failed to load alerts.json: %s", e)
        return []


def listing_matches_alert(listing: Listing, alert: dict) -> bool:
    if "price_max" in alert and listing.price and listing.price > alert["price_max"]:
        return False
    if "price_min" in alert and listing.price and listing.price < alert["price_min"]:
        return False
    if "district" in alert and listing.district:
        if alert["district"].lower() not in listing.district.lower():
            return False
    if alert.get("has_bathtub") and not listing.has_bathtub:
        return False
    if alert.get("pets_allowed") and not listing.pets_allowed:
        return False
    if "metro_max_min" in alert and listing.metro_distance_min is not None:
        if listing.metro_distance_min > alert["metro_max_min"]:
            return False
    if "rooms" in alert and listing.rooms:
        if listing.rooms != alert["rooms"]:
            return False
    return True


async def check_and_notify(db: Session, new_listing_ids: list[int]):
    alerts = load_alerts()
    if not alerts:
        return

    listings = db.query(Listing).filter(Listing.id.in_(new_listing_ids)).all()

    for listing in listings:
        for alert in alerts:
            if listing_matches_alert(listing, alert):
                alert_name = alert.get("name", "Alert")
                logger.info("Listing %s matches alert '%s'", listing.otodom_id, alert_name)
                try:
                    await send_telegram_alert(listing, alert_name)
                except Exception as e:
                    logger.error("Telegram notification failed: %s", e)
                try:
                    await send_email_alert(listing, alert_name)
                except Exception as e:
                    logger.error("Email notification failed: %s", e)
