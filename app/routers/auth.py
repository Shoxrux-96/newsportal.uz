from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, UserStatus, UserRole
from app.auth import hash_password, verify_password, create_access_token, get_current_user_from_cookie

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = get_current_user_from_cookie(request)
    if user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": "Email yoki parol noto'g'ri"
        })

    if user.status == UserStatus.pending:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": "Hisobingiz admin tomonidan tasdiqlanmagan"
        })

    if user.status == UserStatus.rejected:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": "Hisobingiz rad etilgan"
        })

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role
    })

    response = RedirectResponse("/admin" if user.role == UserRole.admin else "/", status_code=302)
    response.set_cookie("access_token", token, httponly=True, max_age=86400)
    return response

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    user = get_current_user_from_cookie(request)
    if user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("auth/signup.html", {"request": request, "error": None, "success": None})

@router.post("/signup", response_class=HTMLResponse)
async def signup(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse("auth/signup.html", {
            "request": request,
            "error": "Parollar mos kelmadi",
            "success": None
        })

    if len(password) < 6:
        return templates.TemplateResponse("auth/signup.html", {
            "request": request,
            "error": "Parol kamida 6 ta belgidan iborat bo'lishi kerak",
            "success": None
        })

    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        return templates.TemplateResponse("auth/signup.html", {
            "request": request,
            "error": "Bu email allaqachon ro'yxatdan o'tgan",
            "success": None
        })

    new_user = User(
        full_name=full_name,
        email=email,
        hashed_password=hash_password(password),
        role=UserRole.user,
        status=UserStatus.pending
    )
    db.add(new_user)
    await db.commit()

    return templates.TemplateResponse("auth/signup.html", {
        "request": request,
        "error": None,
        "success": "Ro'yxatdan muvaffaqiyatli o'tdingiz! Admin tasdiqlashini kuting."
    })

@router.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response
