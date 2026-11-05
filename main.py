from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from client.api import get_car


app = FastAPI(title="Car Deals")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Car Deals"},
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/cars/{car_id}")
async def car_details(car_id: str):
    return await get_car(car_id)
