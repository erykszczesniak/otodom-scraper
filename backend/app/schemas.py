from pydantic import BaseModel
from datetime import datetime, date


class ListingBase(BaseModel):
    otodom_id: str
    url: str
    title: str
    price: float | None = None
    deposit: float | None = None
    agency_fee: bool = False
    rooms: int | None = None
    area: float | None = None
    floor: int | None = None
    total_floors: int | None = None
    district: str | None = None
    address: str | None = None
    has_balcony: bool = False
    has_garden: bool = False
    has_parking: bool = False
    has_elevator: bool = False
    pets_allowed: bool | None = None
    has_bathtub: bool | None = None
    furnished: str | None = None
    heating: str | None = None
    metro_distance_min: int | None = None
    center_distance_min: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    images: str | None = None
    description: str | None = None
    available_from: date | None = None


class ListingCreate(ListingBase):
    pass


class ListingOut(ListingBase):
    id: int
    is_active: bool
    first_seen: datetime
    last_seen: datetime
    last_updated: datetime
    price_history: list["PriceHistoryOut"] = []

    model_config = {"from_attributes": True}


class ListingCard(BaseModel):
    id: int
    otodom_id: str
    url: str
    title: str
    price: float | None = None
    deposit: float | None = None
    agency_fee: bool
    rooms: int | None = None
    area: float | None = None
    district: str | None = None
    has_bathtub: bool | None = None
    pets_allowed: bool | None = None
    metro_distance_min: int | None = None
    center_distance_min: int | None = None
    images: str | None = None
    first_seen: datetime
    is_active: bool

    model_config = {"from_attributes": True}


class PriceHistoryOut(BaseModel):
    id: int
    listing_id: int
    price: float
    recorded_at: datetime

    model_config = {"from_attributes": True}


class ScrapeRunOut(BaseModel):
    id: int
    started_at: datetime
    finished_at: datetime | None = None
    listings_found: int
    listings_new: int
    listings_updated: int
    error: str | None = None

    model_config = {"from_attributes": True}
