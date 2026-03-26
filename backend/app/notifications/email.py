import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib

from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, NOTIFY_EMAIL
from app.models import Listing

logger = logging.getLogger(__name__)


def build_html(listing: Listing, alert_name: str) -> str:
    price_str = f"{listing.price:,.0f}".replace(",", " ") if listing.price else "?"
    return f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #f59e0b;">Nowe ogłoszenie — {alert_name}</h2>
        <h3>{listing.title}</h3>
        <p><strong>Cena:</strong> {price_str} PLN/mies.</p>
        <p><strong>Lokalizacja:</strong> {listing.address or listing.district or '—'}</p>
        <p><strong>Metraż:</strong> {listing.area or '—'} m² | <strong>Pokoje:</strong> {listing.rooms or '—'}</p>
        <p>
            {'🛁 Wanna' if listing.has_bathtub else ''}
            {'🐾 Zwierzęta' if listing.pets_allowed else ''}
            {'🏢 Bez prowizji' if not listing.agency_fee else ''}
        </p>
        <a href="{listing.url}" style="display: inline-block; background: #f59e0b; color: #000; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold;">
            Zobacz ogłoszenie
        </a>
    </div>
    """


async def send_email_alert(listing: Listing, alert_name: str):
    if not SMTP_HOST or not NOTIFY_EMAIL:
        logger.warning("Email not configured, skipping notification")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Nowe ogłoszenie — {alert_name}"
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFY_EMAIL

    html = build_html(listing, alert_name)
    msg.attach(MIMEText(html, "html"))

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        start_tls=True,
    )
    logger.info("Email notification sent for listing %s", listing.otodom_id)
