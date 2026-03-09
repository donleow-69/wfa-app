"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, Request
from fastapi.applications import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .auth import get_optional_user
from .database import init_db
from .models.user import User

# Import models so Base.metadata knows about all tables.
from .models import chat, complaint, compliance, user  # noqa: F401
from .routers import auth_routes, chat as chat_router, complaints, compliance as compliance_router, policies, policy_checker, rights, subscription


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Workplace Fairness", lifespan=lifespan)

# Serve sw.js from root so its scope covers the whole origin
@app.get("/sw.js")
async def service_worker():
    return FileResponse("app/static/sw.js", media_type="application/javascript")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Register routers
app.include_router(auth_routes.router)
app.include_router(rights.router)
app.include_router(complaints.router)
app.include_router(compliance_router.router)
app.include_router(policies.router)
app.include_router(policy_checker.router)
app.include_router(subscription.router)
app.include_router(chat_router.router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: User | None = Depends(get_optional_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})


@app.get("/offline", response_class=HTMLResponse)
async def offline(request: Request):
    return templates.TemplateResponse("offline.html", {"request": request})


@app.get("/.well-known/assetlinks.json")
async def asset_links():
    """Digital Asset Links for Google Play TWA verification.

    Replace the placeholder SHA-256 fingerprint with your actual signing
    certificate fingerprint after building and signing your Android app.
    """
    return JSONResponse([{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
            "namespace": "android_app",
            "package_name": "com.workplacefairness.app",
            "sha256_cert_fingerprints": [
                "16:A0:D4:DB:77:D2:C2:9E:5C:87:58:B4:C3:39:85:24:25:75:15:F4:F8:64:1C:23:33:08:37:51:2C:B6:CB:93"
            ],
        },
    }])


@app.get("/delete-account", response_class=HTMLResponse)
async def delete_account_page(request: Request, user: User | None = Depends(get_optional_user)):
    return templates.TemplateResponse("delete_account.html", {"request": request, "user": user})


@app.post("/delete-account", response_class=HTMLResponse)
async def delete_account(request: Request, user: User | None = Depends(get_optional_user)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/login", status_code=303)
    from .database import get_db
    from sqlalchemy import delete, select
    from .models.chat import ChatMessage
    from .models.complaint import Complaint
    from .models.compliance import ComplianceChecklist, ComplianceItem
    async for db in get_db():
        # Delete compliance items for user's checklists
        checklist_ids = (await db.execute(
            select(ComplianceChecklist.id).where(ComplianceChecklist.user_id == user.id)
        )).scalars().all()
        if checklist_ids:
            await db.execute(delete(ComplianceItem).where(ComplianceItem.checklist_id.in_(checklist_ids)))
        await db.execute(delete(ComplianceChecklist).where(ComplianceChecklist.user_id == user.id))
        await db.execute(delete(ChatMessage).where(ChatMessage.user_id == user.id))
        await db.execute(delete(Complaint).where(Complaint.user_id == user.id))
        await db.execute(delete(User).where(User.id == user.id))
        await db.commit()
    response = templates.TemplateResponse("delete_account.html", {"request": request, "user": None, "success": True})
    response.delete_cookie("session_token")
    return response


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, view: str | None = None, user: User = Depends(get_optional_user)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/login", status_code=303)
    active_view = view if view in ("employee", "employer") else user.role
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "user": user, "active_view": active_view}
    )
