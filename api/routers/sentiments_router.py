from typing import Annotated
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, Path, Response, status
from models.stock_model import Stock
from models.newsArticle_model import NewsArticle
from dependencies.user_dependency import verfiy_api_key

router = APIRouter()


@router.get("/trend/{ticker}")
async def get_sentiment_trend(
    api_key: Annotated[str, Depends(verfiy_api_key)],
    response: Response,
    ticker: Annotated[
        str,
        Path(
            title="Ticker",
            description="The ticker of the stock",
        ),
    ],
    period_start: str | None = Query(
        None,
        description="The start date of the period (YYYY-MM-DD)",
    ),
    period_end: str | None = Query(
        None,
        description="The end date of the period (YYYY-MM-DD)",
    ),
    interval: str = Query(
        default="1d",
        description="The interval of the data (1d, 1wk, 1mo)",
    ),
):

    if not api_key["status"]:
        return api_key

    # Verify stock exists
    if not Stock.objects(ticker=ticker).first():
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "status": False,
            "message": "Stock not found",
        }

    # Validate interval
    valid_intervals = ["1d", "1wk", "1mo"]
    if interval not in valid_intervals:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status": False,
            "message": f"Invalid interval. Must be one of {valid_intervals}",
        }

    try:
        start_date = None
        end_date = None

        if period_start:
            start_date = datetime.strptime(period_start, "%Y-%m-%d")
        if period_end:
            end_date = datetime.strptime(period_end, "%Y-%m-%d")

        if start_date and end_date and end_date < start_date:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "status": False,
                "message": "end_date must be after start_date",
            }

        query = NewsArticle.objects(tickers=ticker)

        if start_date:
            query = query.filter(published_at__gte=start_date)
        if end_date:
            query = query.filter(published_at__lte=end_date)

        news_articles = query.order_by("published_at")

        trend_data = {}

        for article in news_articles:
            relevant_insights = [
                insight for insight in article.insights if insight.ticker == ticker
            ]

            if not relevant_insights:
                continue

            date_key = None
            if interval == "1d":
                date_key = article.published_at.strftime("%Y-%m-%d")
            elif interval == "1wk":
                date_key = (
                    article.published_at
                    - timedelta(days=article.published_at.weekday())
                ).strftime("%Y-%m-%d")
            else:  # 1mo
                date_key = article.published_at.strftime("%Y-%m")

            if date_key not in trend_data:
                trend_data[date_key] = {"count": 0, "sentiment_sum": 0.0}

            for insight in relevant_insights:
                trend_data[date_key]["count"] += 1
                trend_data[date_key]["sentiment_sum"] += insight.sentiment_score

        formatted_data = []
        for date, data in sorted(trend_data.items()):
            avg_sentiment = (
                data["sentiment_sum"] / data["count"] if data["count"] > 0 else 0.0
            )
            formatted_data.append({"s": round(avg_sentiment, 3), "t": date})

        return {"status": True, "data": formatted_data}

    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status": False,
            "message": f"Invalid date format: {str(e)}. Use YYYY-MM-DD",
        }
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status": False,
            "message": f"An error occurred: {str(e)}",
        }
