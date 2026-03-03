"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import Depends, Request
from fastapi.applications import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .auth import get_optional_user
from .database import init_db
from .models.user import User

# Import models so Base.metadata knows about all tables.
from .models import complaint, compliance, user  # noqa: F401
from .routers import auth_routes, complaints, compliance as compliance_router, policies, rights


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="WFA — Workplace Fairness Act", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Register routers
app.include_router(auth_routes.router)
app.include_router(rights.router)
app.include_router(complaints.router)
app.include_router(compliance_router.router)
app.include_router(policies.router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: User | None = Depends(get_optional_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: User = Depends(get_optional_user)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})
