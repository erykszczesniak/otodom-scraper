from fastapi import APIRouter

router = APIRouter(prefix="/api/listings", tags=["listings"])


@router.get("")
async def get_listings():
    return {"message": "Listings endpoint — coming in feature/api-endpoints"}
