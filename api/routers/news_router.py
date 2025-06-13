from typing import Annotated, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response, status

from dependencies.user_dependency import verfiy_api_key
from models.newsArticle_model import NewsArticle
from utils import rename_keys

router = APIRouter()


@router.get("")
async def get_news(
    api_key: Annotated[str, Depends(verfiy_api_key)],
    response: Response,
    ticker: Optional[str] = None,
    from_date: Optional[str] = Query(
        None, alias="from", description="Start date (YYYY-MM-DD)"
    ),
    to_date: Optional[str] = Query(
        None, alias="to", description="End date (YYYY-MM-DD)"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=1000, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    order: Optional[str] = Query(None, description="Sort order (asc or desc)"),
):

    if not api_key["status"]:
        return api_key

    # Start with base query
    news_articles = NewsArticle.objects()

    # Apply filters
    if ticker:
        news_articles = news_articles.filter(tickers=ticker)

    # Date filtering
    try:
        if from_date:
            from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
            news_articles = news_articles.filter(published_at__gte=from_datetime)

        if to_date:
            to_datetime = datetime.strptime(to_date, "%Y-%m-%d")
            to_datetime = to_datetime.replace(hour=23, minute=59, second=59)
            news_articles = news_articles.filter(published_at__lte=to_datetime)
    except ValueError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status": False,
            "message": "Invalid date format. Use YYYY-MM-DD",
        }

    # Apply sorting
    if sort_by:
        # Determine sort direction
        sort_direction = "-" if order and order.lower() == "desc" else ""
        sort_field = f"{sort_direction}{sort_by}"  # eg: "-publishedAt"
        news_articles = news_articles.order_by(sort_field)

    # Get total count before pagination
    total_count = news_articles.count()

    # Apply pagination
    skip = (page - 1) * limit
    news_articles = news_articles.skip(skip).limit(limit)

    # Calculate pagination metadata
    total_pages = (total_count + limit - 1) // limit

    if page > total_pages:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status": False,
            "message": "Page number exceeds total pages",
        }

    # Process results
    key_map = {
        "_id": "id",
        "articleUrl": "article_url",
        "imageUrl": "image_url",
        "publishedAt": "published_at",
        "sentimentReasoning": "sentiment_reasoning",
        "sentimentScore": "sentiment_score",
        "homepageUrl": "homepage_url",
        "logoUrl": "logo_url",
        "createdAt": "created_at",
        "updatedAt": "updated_at",
    }

    news = []
    for news_article in news_articles:
        news_article_dict: dict = news_article.to_mongo().to_dict()
        news_article_dict["_id"] = str(news_article_dict["_id"])
        news_article_dict = rename_keys(news_article_dict, key_map)
        news_article_dict.pop("created_at")
        news_article_dict.pop("updated_at")
        news.append(news_article_dict)

    return {
        "status": True,
        "data": news,
        "pagination": {
            "count": len(news),
            "total": total_count,
            "page": page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }
