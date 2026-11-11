import os
from typing import Any
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv


load_dotenv()

BASE_URL = "https://api.auto.dev"
API_KEY = os.getenv("API_KEY") or os.getenv("AUTO_DEV_API_KEY")


def format_listing(listing: dict[str, Any]) -> dict[str, Any]:
    """Convert an Auto.dev listing into the flat shape used by the app."""
    vehicle = listing.get("vehicle") or {}
    retail = listing.get("retailListing") or {}

    city = retail.get("city")
    state = retail.get("state")
    if city and state:
        location = f"{city}, {state}"
    else:
        location = city or state or listing.get("location")

    return {
        "link": retail.get("vdp") or listing.get("@id"),
        "year": vehicle.get("year"),
        "make": vehicle.get("make"),
        "model": vehicle.get("model"),
        "mileage": retail.get("miles"),
        "price": retail.get("price"),
        "location": location,
    }


async def get_similar_listings(url: str) -> list[dict[str, Any]]:
    """Fetch and format listings from a same-make/model search URL."""
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url, headers=_headers())
        response.raise_for_status()
        results = response.json().get("data", [])
        return [format_listing(listing) for listing in results]


def format_car_details(response: dict[str, Any]) -> dict[str, Any]:
    """Flatten an individual Auto.dev listing for the detail page."""
    listing = response.get("data") or response
    vehicle = listing.get("vehicle") or {}
    retail = listing.get("retailListing") or {}
    make = vehicle.get("make")
    model = vehicle.get("model")

    similar_params = {
        "vehicle.make": make,
        "vehicle.model": model,
        "page": 1,
        "limit": 20,
    }

    return {
        "year": vehicle.get("year"),
        "mileage": retail.get("miles"),
        "city": retail.get("city"),
        "make": make,
        "price": retail.get("price"),
        "type": vehicle.get("type") or vehicle.get("bodyStyle"),
        "url": retail.get("carfaxUrl"),
        "used": retail.get("used"),
        "vin": listing.get("vin") or vehicle.get("vin"),
        "msrp": vehicle.get("baseMsrp"),
        "invoice": vehicle.get("baseInvoice"),
        "similar_listings_url": (
            f"{BASE_URL}/listings?{urlencode(similar_params)}"
            if make and model
            else None
        ),
    }


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
) -> list[dict[str, Any]]:
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
        results = response.json().get("data", [])
        return [format_listing(listing) for listing in results]


async def get_car(car_id: str) -> dict[str, Any]:
    """Fetch one listing using the car ID/VIN returned by Auto.dev."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=20.0) as client:
        response = await client.get(f"/listings/{car_id}", headers=_headers())
        response.raise_for_status()
        return format_car_details(response.json())


async def get_listing_by_vin(vin: str) -> dict[str, Any]:
    """Backward-compatible alias for fetching a listing by VIN."""
    return await get_car(vin)
