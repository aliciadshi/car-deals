import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()

BASE_URL = "https://api.auto.dev"
API_KEY = os.getenv("API_KEY") or os.getenv("AUTO_DEV_API_KEY")


def _headers() -> dict[str, str]:
    if not API_KEY:
        raise RuntimeError("API_KEY is not set in the environment or .env file")

    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


async def search_listings(
    *,
    make: str | None = None,
    model: str | None = None,
    max_price: int | None = None,
    zip_code: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "page": page,
        "limit": limit,
    }

    if make:
        params["vehicle.make"] = make
    if model:
        params["vehicle.model"] = model
    if max_price is not None:
        params["retailListing.price"] = f"1-{max_price}"
    if zip_code:
        params["zip"] = zip_code

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=20.0) as client:
        response = await client.get("/listings", headers=_headers(), params=params)
        response.raise_for_status()
        return response.json()


async def get_car(car_id: str) -> dict[str, Any]:
    """Fetch one listing using the car ID/VIN returned by Auto.dev."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=20.0) as client:
        response = await client.get(f"/listings/{car_id}", headers=_headers())
        response.raise_for_status()
        return response.json()


async def get_listing_by_vin(vin: str) -> dict[str, Any]:
    """Backward-compatible alias for fetching a listing by VIN."""
    return await get_car(vin)
