from typing import Annotated

import yfinance as yf
from fastapi import APIRouter, Depends, Path, status, Query, Response

from dependencies.user_dependency import verfiy_api_key

router = APIRouter()


@router.get("/{ticker}")
async def get_quotes(
    api_key: Annotated[str, Depends(verfiy_api_key)],
    response: Response,
    ticker: Annotated[
        str, Path(description="The stock ticker symbol (e.g., AAPL, GOOGL, MSFT).")
    ],
    period: str | None = Query(
        None, description="Defines the range of historical data to fetch."
    ),
    interval: str | None = Query(
        None, description="Time granularity of the data points."
    ),
    start: str | None = Query(
        None, description="Start date of the requested data range in ISO 8601 format."
    ),
    end: str | None = Query(
        None, description="End date of the requested data range in ISO 8601 format."
    ),
):
    if not api_key["status"]:
        return api_key

    try:
        tkr = yf.Ticker(ticker)
        quotes = tkr.history(
            period=period or "1mo", interval=interval or "1d", start=start, end=end
        )
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": False, "message": str(e)}

    quotes_dict = (
        quotes[["Open", "Close", "High", "Low", "Volume"]]
        .round(2)
        .to_dict(orient="index")
    )

    quotes_arr = []

    for quote in quotes_dict.items():
        quotes_arr.append(
            {
                "o": quote[1]["Open"],
                "c": quote[1]["Close"],
                "h": quote[1]["High"],
                "l": quote[1]["Low"],
                "v": quote[1]["Volume"],
                "t": int(quote[0].timestamp() * 1000),
            }
        )

    return {
        "status": True,
        "data": quotes_arr,
    }
