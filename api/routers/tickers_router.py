from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Response, status, Path, Query

from dependencies.user_dependency import verfiy_api_key
from models.stock_model import Stock
from models.index_model import Index

from utils import rename_keys

router = APIRouter()

key_map = {
    "_id": "id",
    "companyName": "company_name",
    "logoUrl": "logo_url",
    "zipCode": "zip_code",
    "yearBorn": "year_born",
    "maxAge": "max_age",
    "exercisedValue": "exercised_value",
    "unexercisedValue": "unexercised_value",
    "marketCap": "market_cap",
    "companyOfficers": "company_officers",
    "exchangeName": "exchange_name",
    "createdAt": "created_at",
    "updatedAt": "updated_at",
}


@router.get("")
async def get_tickers(
    api_key: Annotated[dict, Depends(verfiy_api_key)],
    response: Response,
    market: str | None = Query(
        None,
        description="Filter by market type (`stocks`, `indices`). By default all markets are included.",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    order: Optional[str] = Query("asc", description="Sort order (`asc` or `desc`)"),
):
    if not api_key["status"]:
        return api_key

    tickers = []

    # Fetch all data based on market filter
    if market == "stocks":
        tickers = list(Stock.objects.all())
    elif market == "indices":
        tickers = list(Index.objects.all())
    else:
        tickers = list(Stock.objects.all()) + list(Index.objects.all())

    total_count = len(tickers)

    # Sort in memory
    if sort_by:
        reverse = order.lower() == "desc"
        tickers = sorted(
            tickers,
            key=lambda x: x.to_mongo().to_dict().get(sort_by, 0),
            reverse=reverse,
        )

    # Paginate in memory
    start = (page - 1) * limit
    end = start + limit
    paginated_tickers = tickers[start:end]

    # Handle out-of-range pages
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
    if page > total_pages and total_pages > 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": False, "message": "Page number exceeds total pages"}

    # Clean and transform
    processed_tickers = []
    for doc in paginated_tickers:
        doc = doc.to_mongo().to_dict()
        doc["_id"] = str(doc["_id"])
        processed_doc = rename_keys(doc, key_map)
        processed_doc.pop("created_at", None)
        processed_doc.pop("updated_at", None)
        processed_tickers.append(processed_doc)

    return {
        "status": True,
        "data": processed_tickers,
        "pagination": {
            "count": len(processed_tickers),
            "total": total_count,
            "page": page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }


@router.get("/{ticker}")
async def get_ticker(
    api_key: Annotated[dict, Depends(verfiy_api_key)],
    response: Response,
    tkr: Annotated[
        str, Path(alias="ticker", title="Ticker", description="Ticker of the stock")
    ],
):

    if not api_key["status"]:
        return api_key

    ticker = Stock.objects(ticker=tkr).first()

    if not ticker:
        ticker = Index.objects(ticker=tkr).first()

    if not ticker:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "status": False,
            "message": "Ticker not found",
        }

    ticker: dict = ticker.to_mongo().to_dict()
    ticker["_id"] = str(ticker["_id"])
    ticker = rename_keys(ticker, key_map)
    ticker.pop("created_at", None)
    ticker.pop("updated_at", None)

    return {
        "status": True,
        "data": ticker,
    }
