from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import News, User, NewsCategory
from app.auth import get_current_user_from_cookie, slugify
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    result = await db.execute(
        select(News, User).join(User).where(News.is_published == True)
        .order_by(News.created_at.desc()).limit(6)
    )
    news_list = result.all()
    
    # Category counts
    cat_result = await db.execute(
        select(News.category, func.count(News.id)).where(News.is_published == True)
        .group_by(News.category)
    )
    categories = cat_result.all()
    
    return templates.TemplateResponse("home/index.html", {
        "request": request,
        "news_list": news_list,
        "categories": categories,
        "current_user": user
    })

@router.get("/news", response_class=HTMLResponse)
async def news_list(request: Request, category: str = None, page: int = 1, db: AsyncSession = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    per_page = 9
    offset = (page - 1) * per_page

    query = select(News, User).join(User).where(News.is_published == True)
    if category:
        query = query.where(News.category == category)
    
    count_q = select(func.count(News.id)).where(News.is_published == True)
    if category:
        count_q = count_q.where(News.category == category)

    total_result = await db.execute(count_q)
    total = total_result.scalar()
    total_pages = (total + per_page - 1) // per_page

    result = await db.execute(query.order_by(News.created_at.desc()).offset(offset).limit(per_page))
    news_items = result.all()

    return templates.TemplateResponse("news/list.html", {
        "request": request,
        "news_items": news_items,
        "current_user": user,
        "category": category,
        "categories": [c.value for c in NewsCategory],
        "page": page,
        "total_pages": total_pages,
    })

@router.get("/news/{slug}", response_class=HTMLResponse)
async def news_detail(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    result = await db.execute(
        select(News, User).join(User).where(News.slug == slug, News.is_published == True)
    )
    item = result.first()
    if not item:
        raise HTTPException(404, "Yangilik topilmadi")
    
    news, author = item
    news.views += 1
    await db.commit()

    # Related news
    related_result = await db.execute(
        select(News).where(News.category == news.category, News.id != news.id, News.is_published == True)
        .order_by(News.created_at.desc()).limit(3)
    )
    related = related_result.scalars().all()

    return templates.TemplateResponse("news/detail.html", {
        "request": request,
        "news": news,
        "author": author,
        "related": related,
        "current_user": user
    })
