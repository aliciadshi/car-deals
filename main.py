import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from charts import depreciation_chart, price_mileage_chart
from client.api import get_car, get_similar_listings, search_listings


app = FastAPI(title="Car Deals")
templates = Jinja2Templates(directory="templates")
app.mount(
    "/browse-static",
    StaticFiles(directory="templates/browse"),
    name="browse-static",
)
app.mount(
    "/detail-static",
    StaticFiles(directory="templates/detail"),
    name="detail-static",
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Car Deals"},
    )


@app.get("/browse", response_class=HTMLResponse)
async def browse(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="browse/browse.html",
        context={"title": "Browse cars"},
    )


def format_money(value: int | float | None) -> str:
    if value is None:
        return "—"
    return f"${int(value):,}"


def format_miles(value: int | float | None) -> str:
    if value is None:
        return "—"
    return f"{int(value):,} mi"


def car_subtitle(car: dict) -> str:
    if car.get("used") is True:
        condition = "Used listing"
    elif car.get("used") is False:
        condition = "New listing"
    else:
        condition = "Listing"
    parts = [condition]
    if car.get("type"):
        parts.append(str(car["type"]))
    if car.get("location"):
        parts.append(str(car["location"]))
    return "  ·  ".join(parts)


@app.get("/detail", response_class=HTMLResponse)
async def detail(request: Request, vin: str | None = None):
    car = None
    similar: list[dict] = []
    if vin:
        try:
            car = await get_car(vin)
        except httpx.HTTPError:
            car = None
        if not car or not car.get("vin"):
            car = None
        elif car.get("similar_listings_url"):
            try:
                similar = await get_similar_listings(car["similar_listings_url"])
            except httpx.HTTPError:
                similar = []
            similar = [item for item in similar if item.get("vin") != car["vin"]]

    title = "Car"
    depreciation = ""
    price_mileage = ""
    if car:
        title = " ".join(
            str(part)
            for part in (car.get("year"), car.get("make"), car.get("model"))
            if part
        )
        if car.get("msrp"):
            depreciation = depreciation_chart(int(car["msrp"]))
        if car.get("mileage") is not None and car.get("price") is not None:
            price_mileage = price_mileage_chart(
                int(car["mileage"]),
                int(car["price"]),
                similar,
            )

    return templates.TemplateResponse(
        request=request,
        name="detail/detail.html",
        context={
            "title": title,
            "car": car,
            "similar": similar,
            "subtitle": car_subtitle(car) if car else "",
            "format_money": format_money,
            "format_miles": format_miles,
            "depreciation_chart": depreciation,
            "price_mileage_chart": price_mileage,
        },
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/cars/{car_id}/similar")
async def similar_cars(car_id: str):
    car = await get_car(car_id)
    similar_url = car.get("similar_listings_url")
    if not similar_url:
        return []
    return await get_similar_listings(similar_url)


@app.get("/api/cars/{car_id}")
async def car_details(car_id: str):
    return await get_car(car_id)


@app.get("/api/cars")
async def search_cars(
    make: str | None = None,
    model: str | None = None,
    max_price: int | None = None,
    zip_code: str | None = None,
    page: int = 1,
    limit: int = 20,
):
    return await search_listings(
        make=make,
        model=model,
        max_price=max_price,
        zip_code=zip_code,
        page=page,
        limit=limit,
    )
