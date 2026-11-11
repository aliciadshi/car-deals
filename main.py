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


@app.get("/detail", response_class=HTMLResponse)
async def detail(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="detail/detail.html",
        context={
            "title": "2023 Subaru BRZ",
            "depreciation_chart": depreciation_chart(),
            "price_mileage_chart": price_mileage_chart(),
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
