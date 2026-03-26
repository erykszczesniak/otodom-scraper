from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Listing, PriceHistory
from app.schemas import ListingOut, ListingCard, PriceHistoryOut
from app.format_utils import format_response

router = APIRouter(prefix="/api/listings", tags=["listings"])


@router.get("")
async def get_listings(
    format: str = Query("json", pattern="^(json|xml|csv)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    price_min: float | None = None,
    price_max: float | None = None,
    area_min: float | None = None,
    area_max: float | None = None,
    rooms: list[int] = Query(None),
    district: str | None = None,
    has_bathtub: bool | None = None,
    pets_allowed: bool | None = None,
    agency_fee: bool | None = None,
    metro_max_min: int | None = None,
    center_max_min: int | None = None,
    deposit_max: float | None = None,
    furnished: str | None = Query(None, pattern="^(yes|no|partially)$"),
    sort_by: str = Query("first_seen", pattern="^(price|area|metro_distance|first_seen)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    q = db.query(Listing).filter(Listing.is_active == True)  # noqa: E712

    if price_min is not None:
        q = q.filter(Listing.price >= price_min)
    if price_max is not None:
        q = q.filter(Listing.price <= price_max)
    if area_min is not None:
        q = q.filter(Listing.area >= area_min)
    if area_max is not None:
        q = q.filter(Listing.area <= area_max)
    if rooms:
        q = q.filter(Listing.rooms.in_(rooms))
    if district:
        q = q.filter(Listing.district.ilike(f"%{district}%"))
    if has_bathtub is not None:
        q = q.filter(Listing.has_bathtub == has_bathtub)
    if pets_allowed is not None:
        q = q.filter(Listing.pets_allowed == pets_allowed)
    if agency_fee is not None:
        q = q.filter(Listing.agency_fee == agency_fee)
    if metro_max_min is not None:
        q = q.filter(
            (Listing.metro_distance_min.is_(None)) | (Listing.metro_distance_min <= metro_max_min)
        )
    if center_max_min is not None:
        q = q.filter(
            (Listing.center_distance_min.is_(None)) | (Listing.center_distance_min <= center_max_min)
        )
    if deposit_max is not None:
        q = q.filter(
            (Listing.deposit.is_(None)) | (Listing.deposit <= deposit_max)
        )
    if furnished:
        q = q.filter(Listing.furnished == furnished)

    sort_map = {
        "price": Listing.price,
        "area": Listing.area,
        "metro_distance": Listing.metro_distance_min,
        "first_seen": Listing.first_seen,
    }
    sort_col = sort_map[sort_by]
    q = q.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())

    total = q.count()
    pages = (total + per_page - 1) // per_page
    items = q.offset((page - 1) * per_page).limit(per_page).all()

    cards = [ListingCard.model_validate(item).model_dump(mode="json") for item in items]

    if format != "json":
        return await format_response(cards, format, "listings", total=total, page=page)

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
        "items": cards,
    }


@router.get("/{listing_id}")
async def get_listing(
    listing_id: int,
    format: str = Query("json", pattern="^(json|xml)$"),
    db: Session = Depends(get_db),
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    out = ListingOut.model_validate(listing).model_dump(mode="json")

    if format == "xml":
        return await format_response(out, format, f"listing_{listing_id}")

    return out


@router.get("/{listing_id}/price-history", response_model=list[PriceHistoryOut])
async def get_price_history(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    history = (
        db.query(PriceHistory)
        .filter(PriceHistory.listing_id == listing_id)
        .order_by(PriceHistory.recorded_at.asc())
        .all()
    )
    return history


@router.get("/stats/overview")
async def get_stats(db: Session = Depends(get_db)):
    active = db.query(Listing).filter(Listing.is_active == True)  # noqa: E712
    count_active = active.count()

    if count_active == 0:
        return {
            "count_active": 0,
            "avg_price": None,
            "median_price": None,
            "price_per_m2_avg": None,
            "count_with_bathtub": 0,
            "count_pets_allowed": 0,
        }

    avg_price = db.query(func.avg(Listing.price)).filter(
        Listing.is_active == True, Listing.price.isnot(None)  # noqa: E712
    ).scalar()

    prices = [
        r[0]
        for r in db.query(Listing.price)
        .filter(Listing.is_active == True, Listing.price.isnot(None))  # noqa: E712
        .order_by(Listing.price)
        .all()
    ]
    median_price = prices[len(prices) // 2] if prices else None

    rows_with_area = (
        db.query(Listing.price, Listing.area)
        .filter(
            Listing.is_active == True,  # noqa: E712
            Listing.price.isnot(None),
            Listing.area.isnot(None),
            Listing.area > 0,
        )
        .all()
    )
    if rows_with_area:
        price_per_m2_avg = sum(r[0] / r[1] for r in rows_with_area) / len(rows_with_area)
    else:
        price_per_m2_avg = None

    count_with_bathtub = active.filter(Listing.has_bathtub == True).count()  # noqa: E712
    count_pets_allowed = active.filter(Listing.pets_allowed == True).count()  # noqa: E712

    return {
        "count_active": count_active,
        "avg_price": round(avg_price, 2) if avg_price else None,
        "median_price": median_price,
        "price_per_m2_avg": round(price_per_m2_avg, 2) if price_per_m2_avg else None,
        "count_with_bathtub": count_with_bathtub,
        "count_pets_allowed": count_pets_allowed,
    }
