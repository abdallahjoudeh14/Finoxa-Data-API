from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status, Response

from models.stock_model import Stock
from models.newsArticle_model import NewsArticle
from models.index_model import Index

from dependencies.user_dependency import verfiy_api_key
from utils import rename_keys

router = APIRouter()

stock_key_map = {
    "_id": "id",
    "companyName": "company_name",
}

news_article_key_map = {
    "_id": "id",
    "articleUrl": "article_url",
    "publishedAt": "published_at",
}


@router.get("")
async def search(
    api_key: Annotated[str, Depends(verfiy_api_key)],
    response: Response,
    q: str | None = Query(
        None, description="A query string to search for stocks, indices, and news."
    ),
    type_: str | None = Query(
        None,
        alias="type",
        description="Specifies the type of data to search for (e.g., stocks, indices, news). If not provided, it will search for all.",
    ),
    from_date: str | None = Query(
        None,
        alias="from",
        description="Return results published after this date. Works only with `news`.",
    ),
    to_date: str | None = Query(
        None,
        alias="to",
        description="Return results published before this date. Works only with `news`.",
    ),
    source: str | None = Query(
        None,
        description="Specifies the news provider or source (e.g., `Yahoo Finance`).",
    ),
):

    if not api_key["status"]:
        return api_key

    if not q or len(q) == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status": False,
            "message": "Please provide a search query.",
        }

        # Initialize empty results
    stocks = []
    indices = []
    news_articles = []

    # Search for stocks if type is not specified or type is 'stocks'
    if (not type_ or type_.lower() == "stocks") and len(q) < 15:
        stocks: list[dict] = Stock.objects.aggregate(
            [
                {
                    "$search": {
                        "index": "stocks",
                        "text": {
                            "query": q,
                            "path": [
                                "ticker",
                                "companyName",
                            ],
                        },
                    }
                },
                {"$limit": 5},
                {
                    "$project": {
                        "_id": 1,
                        "ticker": 1,
                        "companyName": 1,
                        "market": 1,
                    }
                },
            ]
        ).to_list()

    # Search for indices if type is not specified or type is 'indices'
    if (not type_ or type_.lower() == "indices") and len(q) < 15:
        indices: list[dict] = Index.objects.aggregate(
            [
                {
                    "$search": {
                        "index": "indices",
                        "text": {
                            "query": q,
                            "path": [
                                "ticker",
                                "name",
                            ],
                        },
                    }
                },
                {"$limit": 5},
                {
                    "$project": {
                        "_id": 1,
                        "ticker": 1,
                        "name": 1,
                        "market": 1,
                    }
                },
            ]
        ).to_list()

    # Search for news if type is not specified or type is 'news'
    if not type_ or type_.lower() == "news":
        # Prepare aggregation pipeline for news search
        news_pipeline = [
            {
                "$search": {
                    "index": "news_articles",
                    "text": {
                        "query": q,
                        "path": "title",
                    },
                }
            },
            {"$limit": 5},
            {
                "$project": {
                    "_id": 1,
                    "title": 1,
                    "articleUrl": 1,
                    "publishedAt": 1,
                    "publisher.name": 1,
                }
            },
        ]

        # Add date filters for news articles if provided
        date_match = {}
        if from_date:
            try:
                from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
                date_match["publishedAt"] = {"$gte": from_datetime}
            except ValueError:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {
                    "status": False,
                    "message": "Invalid date format. Use YYYY-MM-DD",
                }

        if to_date:
            try:
                to_datetime = datetime.strptime(to_date, "%Y-%m-%d")
                to_datetime = to_datetime.replace(hour=23, minute=59, second=59)
                if "publishedAt" in date_match:
                    date_match["publishedAt"]["$lte"] = to_datetime
                else:
                    date_match["publishedAt"] = {"$lte": to_datetime}
            except ValueError:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {
                    "status": False,
                    "message": "Invalid date format. Use YYYY-MM-DD",
                }

        # Add source filter for news articles if provided
        if source:
            if date_match:
                date_match["publisher.name"] = source
            else:
                date_match = {"publisher.name": source}

        # Add match stage to pipeline if we have date or source filters
        if date_match:
            news_pipeline.insert(1, {"$match": date_match})

        # Execute the news search
        news_articles: list[dict] = NewsArticle.objects.aggregate(
            news_pipeline
        ).to_list()

    if stocks:
        for stock in stocks:
            stock["_id"] = str(stock["_id"])
        stocks = rename_keys(stocks, stock_key_map)

    if indices:
        for index in indices:
            index["_id"] = str(index["_id"])
        indices = rename_keys(indices, {"_id": "id"})

    for article in news_articles:
        article["_id"] = str(article["_id"])
    news_articles = rename_keys(news_articles, news_article_key_map)

    return {
        "status": True,
        "data": {
            "stocks": stocks,
            "indices": indices,
            "news": news_articles,
        },
    }
