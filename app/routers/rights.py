"""Employee rights information pages."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..auth import get_optional_user
from ..models.user import User
from .rights_data import COUNTRY_NAMES, RIGHTS_BY_COUNTRY

router = APIRouter(prefix="/rights")
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def rights_overview(
    request: Request,
    country: str | None = None,
    user: User | None = Depends(get_optional_user),
):
    if country and country in RIGHTS_BY_COUNTRY:
        selected = country
    elif user and user.country in RIGHTS_BY_COUNTRY:
        selected = user.country
    else:
        selected = "us"

    categories = RIGHTS_BY_COUNTRY[selected]
    return templates.TemplateResponse(
        "rights.html",
        {
            "request": request,
            "user": user,
            "categories": categories,
            "countries": COUNTRY_NAMES,
            "selected_country": selected,
        },
    )


@router.get("/{category_id}", response_class=HTMLResponse)
async def rights_detail(
    category_id: str,
    request: Request,
    country: str | None = None,
    user: User | None = Depends(get_optional_user),
):
    if country and country in RIGHTS_BY_COUNTRY:
        selected = country
    elif user and user.country in RIGHTS_BY_COUNTRY:
        selected = user.country
    else:
        selected = "us"

    categories = RIGHTS_BY_COUNTRY[selected]
    category = next((c for c in categories if c["id"] == category_id), None)
    if not category:
        return templates.TemplateResponse(
            "404.html", {"request": request, "user": user}, status_code=404
        )
    return templates.TemplateResponse(
        "rights_detail.html",
        {
            "request": request,
            "user": user,
            "category": category,
            "selected_country": selected,
            "country_name": COUNTRY_NAMES[selected],
        },
    )
