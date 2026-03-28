from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from app.database import init_db, AsyncSessionLocal
from app.models import User, UserRole, UserStatus
from app.auth import hash_password
from sqlalchemy import select

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await create_default_admin()
    yield

async def create_default_admin():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "admin@news.uz"))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                full_name="Super Admin",
                email="admin@news.uz",
                hashed_password=hash_password("admin123"),
                role=UserRole.admin,
                status=UserStatus.approved
            )
            db.add(admin)
            await db.commit()
            print("✅ Default admin created: admin@news.uz / admin123")

app = FastAPI(title="News Portal", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

from app.routers import auth, news, admin
app.include_router(auth.router)
app.include_router(news.router)
app.include_router(admin.router)
