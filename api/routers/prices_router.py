from typing import Annotated

import yfinance as yf
from fastapi import APIRouter, Response, Depends, Path, status, Query

from dependencies.user_dependency import verfiy_api_key

router = APIRouter()


@router.get("/{ticker}")
async def get_prices(
    api_key: Annotated[str, Depends(verfiy_api_key)],
    response: Response,
    ticker: Annotated[
        str, Path(description="The stock ticker symbol (e.g., AAPL, GOOGL, MSFT).")
    ],
):
    if not api_key["status"]:
        return api_key

    try:
        tkr = yf.Ticker(ticker)
        prices = {
            "price": tkr.info.get("currentPrice", tkr.info["regularMarketPrice"]),
            "price_change": tkr.info["regularMarketChange"],
            "price_change_percent": tkr.info["regularMarketChangePercent"],
            "volume": tkr.info["volume"],
            "avg_volume": tkr.info["averageVolume"],
        }
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": False, "message": str(e)}

    return {
        "status": True,
        "data": prices,
    }


@router.get("")
async def get_prices_bulk(
    api_key: Annotated[str, Depends(verfiy_api_key)],
    response: Response,
    tickers: str | None = Query(
        None,
        description="Comma-separated list of tickers (e.g., AAPL,GOOGL,MSFT).",
    ),
):
    if not api_key["status"]:
        return api_key

    if not tickers:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": False, "message": "No tickers provided"}

    try:
        tickers = tickers.split(",")
        prices = {}
        for ticker in tickers:
            tkr = yf.Ticker(ticker)
            prices[ticker] = {
                "price": tkr.info.get(
                    "currentPrice", tkr.info.get("regularMarketPrice", 0)
                ),
                "price_change": tkr.info.get("regularMarketChange", 0),
                "price_change_percent": tkr.info.get("regularMarketChangePercent", 0),
                "volume": tkr.info.get("volume", 0),
                "avg_volume": tkr.info.get("averageVolume", 0),
            }
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": False, "message": str(e)}
    return {
        "status": True,
        "data": prices,
    }
