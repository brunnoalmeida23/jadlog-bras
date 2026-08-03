from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os


router = APIRouter(prefix="", tags=["Home"])

templates_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "templates",
)

templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={},
    )