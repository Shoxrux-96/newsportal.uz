from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import News, User, UserStatus, UserRole, NewsCategory
from app.auth import get_current_user_from_cookie, slugify
from datetime import datetime

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")

def require_admin(request: Request):
    user = get_current_user_from_cookie(request)
    if not user or user.get("role") != UserRole.admin:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    return user

@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    user = require_admin(request)
    
    news_count = (await db.execute(select(func.count(News.id)))).scalar()
    user_count = (await db.execute(select(func.count(User.id)))).scalar()
    pending_count = (await db.execute(select(func.count(User.id)).where(User.status == UserStatus.pending))).scalar()
    
    recent_news = (await db.execute(
        select(News).order_by(News.created_at.desc()).limit(5)
    )).scalars().all()
    
    pending_users = (await db.execute(
        select(User).where(User.status == UserStatus.pending).order_by(User.created_at.desc())
    )).scalars().all()

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "current_user": user,
        "news_count": news_count,
        "user_count": user_count,
        "pending_count": pending_count,
        "recent_news": recent_news,
        "pending_users": pending_users
    })

@router.get("/news", response_class=HTMLResponse)
async def admin_news_list(request: Request, db: AsyncSession = Depends(get_db)):
    user = require_admin(request)
    result = await db.execute(
        select(News, User).join(User).order_by(News.created_at.desc())
    )
    news_list = result.all()
    return templates.TemplateResponse("admin/news_list.html", {
        "request": request,
        "news_list": news_list,
        "current_user": user
    })

@router.get("/news/create", response_class=HTMLResponse)
async def admin_create_news_page(request: Request):
    user = require_admin(request)
    return templates.TemplateResponse("admin/news_form.html", {
        "request": request,
        "current_user": user,
        "categories": [c for c in NewsCategory],
        "news": None,
        "error": None
    })

@router.post("/news/create", response_class=HTMLResponse)
async def admin_create_news(
    request: Request,
    title: str = Form(...),
    summary: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
    image_url: str = Form(default="/static/images/default.jpg"),
    db: AsyncSession = Depends(get_db)
):
    user = require_admin(request)
    
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while True:
        existing = (await db.execute(select(News).where(News.slug == slug))).scalar_one_or_none()
        if not existing:
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    news = News(
        title=title,
        slug=slug,
        summary=summary,
        content=content,
        category=category,
        image_url=image_url or "/static/images/default.jpg",
        author_id=int(user["sub"]),
        is_published=True
    )
    db.add(news)
    await db.commit()
    return RedirectResponse("/admin/news", status_code=302)

@router.get("/news/{news_id}/edit", response_class=HTMLResponse)
async def admin_edit_news_page(news_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = require_admin(request)
    news = (await db.execute(select(News).where(News.id == news_id))).scalar_one_or_none()
    if not news:
        raise HTTPException(404)
    return templates.TemplateResponse("admin/news_form.html", {
        "request": request,
        "current_user": user,
        "categories": [c for c in NewsCategory],
        "news": news,
        "error": None
    })

@router.post("/news/{news_id}/edit", response_class=HTMLResponse)
async def admin_edit_news(
    news_id: int, request: Request,
    title: str = Form(...),
    summary: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
    image_url: str = Form(default=""),
    db: AsyncSession = Depends(get_db)
):
    user = require_admin(request)
    news = (await db.execute(select(News).where(News.id == news_id))).scalar_one_or_none()
    if not news:
        raise HTTPException(404)
    
    news.title = title
    news.summary = summary
    news.content = content
    news.category = category
    if image_url:
        news.image_url = image_url
    news.updated_at = datetime.utcnow()
    await db.commit()
    return RedirectResponse("/admin/news", status_code=302)

@router.get("/news/{news_id}/delete")
async def admin_delete_news(news_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = require_admin(request)
    news = (await db.execute(select(News).where(News.id == news_id))).scalar_one_or_none()
    if news:
        await db.delete(news)
        await db.commit()
    return RedirectResponse("/admin/news", status_code=302)

@router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, db: AsyncSession = Depends(get_db)):
    user = require_admin(request)
    users = (await db.execute(select(User).order_by(User.created_at.desc()))).scalars().all()
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "users": users,
        "current_user": user,
        "UserStatus": UserStatus,
        "UserRole": UserRole
    })

@router.get("/users/{user_id}/approve")
async def approve_user(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    target = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if target:
        target.status = UserStatus.approved
        await db.commit()
    return RedirectResponse("/admin/users", status_code=302)

@router.get("/users/{user_id}/reject")
async def reject_user(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    target = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if target:
        target.status = UserStatus.rejected
        await db.commit()
    return RedirectResponse("/admin/users", status_code=302)

@router.get("/users/{user_id}/make-admin")
async def make_admin(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    require_admin(request)
    target = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if target:
        target.role = UserRole.admin
        target.status = UserStatus.approved
        await db.commit()
    return RedirectResponse("/admin/users", status_code=302)
