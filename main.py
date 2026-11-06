from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from charts import depreciation_chart, price_mileage_chart
from client.api import get_car


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
        "index.html",
        {"request": request, "title": "Car Deals"},
    )


@app.get("/browse", response_class=HTMLResponse)
async def browse(request: Request):
    return templates.TemplateResponse(
        "browse/browse.html",
        {"request": request, "title": "Browse cars"},
    )


@app.get("/detail", response_class=HTMLResponse)
async def detail(request: Request):
    return templates.TemplateResponse(
        "detail/detail.html",
        {
            "request": request,
            "title": "2023 Subaru BRZ",
            "depreciation_chart": depreciation_chart(),
            "price_mileage_chart": price_mileage_chart(),
        },
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/cars/{car_id}")
async def car_details(car_id: str):
    return await get_car(car_id)
