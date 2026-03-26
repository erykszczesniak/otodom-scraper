from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    otodom_id = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    deposit = Column(Float, nullable=True)
    agency_fee = Column(Boolean, default=False)
    rooms = Column(Integer, nullable=True)
    area = Column(Float, nullable=True)
    floor = Column(Integer, nullable=True)
    total_floors = Column(Integer, nullable=True)
    district = Column(String, nullable=True)
    address = Column(String, nullable=True)
    has_balcony = Column(Boolean, default=False)
    has_garden = Column(Boolean, default=False)
    has_parking = Column(Boolean, default=False)
    has_elevator = Column(Boolean, default=False)
    pets_allowed = Column(Boolean, nullable=True)
    has_bathtub = Column(Boolean, nullable=True)
    furnished = Column(String, nullable=True)
    heating = Column(String, nullable=True)
    metro_distance_min = Column(Integer, nullable=True)
    center_distance_min = Column(Integer, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    images = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    available_from = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

    price_history = relationship("PriceHistory", back_populates="listing")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="price_history")


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    listings_found = Column(Integer, default=0)
    listings_new = Column(Integer, default=0)
    listings_updated = Column(Integer, default=0)
    error = Column(Text, nullable=True)
