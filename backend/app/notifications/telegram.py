import httpx
import logging

from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from app.models import Listing

logger = logging.getLogger(__name__)


def format_message(listing: Listing, alert_name: str) -> str:
    price_str = f"{listing.price:,.0f}".replace(",", " ") if listing.price else "?"
    deposit_str = f"{listing.deposit:,.0f}".replace(",", " ") if listing.deposit else "?"

    lines = [
        f"🏠 *Nowe ogłoszenie — {alert_name}*",
        "",
    ]

    if listing.address or listing.district:
        addr = listing.address or listing.district
        lines.append(f"📍 {addr}")

    lines.append(f"💰 {price_str} PLN/mies. | Kaucja: {deposit_str} PLN")

    details = []
    if listing.area:
        details.append(f"{listing.area} m²")
    if listing.rooms:
        details.append(f"{listing.rooms} pokoje")
    if listing.floor is not None:
        floor_str = str(listing.floor)
        if listing.total_floors:
            floor_str += f"/{listing.total_floors}"
        details.append(f"piętro {floor_str}")
    if details:
        lines.append(f"📐 {' | '.join(details)}")

    badges = []
    if listing.has_bathtub:
        badges.append("🛁 Wanna ✅")
    if listing.pets_allowed:
        badges.append("🐾 Zwierzęta ✅")
    if not listing.agency_fee:
        badges.append("🏢 Bez prowizji ✅")
    if badges:
        lines.append(" | ".join(badges))

    if listing.metro_distance_min is not None:
        lines.append(f"🚇 {listing.metro_distance_min} min do metra")
    if listing.center_distance_min is not None:
        lines.append(f"🏙️ {listing.center_distance_min} min do centrum")

    lines.append("")
    lines.append(f"🔗 [Zobacz ogłoszenie]({listing.url})")

    return "\n".join(lines)


async def send_telegram_alert(listing: Listing, alert_name: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured, skipping notification")
        return

    text = format_message(listing, alert_name)

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
        )
        resp.raise_for_status()
        logger.info("Telegram notification sent for listing %s", listing.otodom_id)
