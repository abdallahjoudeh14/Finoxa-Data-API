import os
import sys
import time
import logging

import schedule
import requests
from requests.exceptions import HTTPError
import yfinance as yf

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from models.stock_model import Stock

from configs.db import connect_db
from utils.logger_util import logger


LOG_SCRAPER_FILE = os.path.join(os.getcwd(), r"logs\stocks_scraper.log")

file_handler = logging.FileHandler(filename=LOG_SCRAPER_FILE)
file_handler.setFormatter(
    logging.Formatter("[%(asctime)s] - [%(levelname)s] - %(message)s")
)
logger.addHandler(file_handler)


def scrape_stocks():

    connect_db()

    logger.info("=" * 50)
    logger.info("Starting Stocks Scraper")
    logger.info("=" * 50)

    api_url = "https://stockanalysis.com/api/screener/s/f?m=s&s=desc&c=s&sc=industry&cn=6000&p=1&i=stocks"
    stocks = requests.get(api_url).json()
    for stock in stocks["data"]["data"]:
        logger.info(f"Scraping {stock['s']} stock")
        try:
            stock_info = yf.Ticker(stock["s"]).info

            required_fields = ["symbol", "longName"]
            if not all(key in stock_info for key in required_fields):
                logger.error(f"Skipping {stock['s']} due to missing required fields.")
                continue

        except (KeyError, HTTPError, requests.exceptions.RequestException) as e:
            logger.error(f"Skipping {stock['s']} due to fetch error: {e}")
            continue
        except Exception as e:
            logger.error(f"Unhandled error for {stock['s']}: {e}")
            continue

        existing_stock = Stock.objects(ticker=stock["s"]).first()
        if existing_stock:
            existing_stock.update(
                employees=stock_info.get("fullTimeEmployees"),
                company_officers=stock_info.get("companyOfficers"),
                market_cap=stock_info.get("marketCap"),
            )
            logger.info(f"Updated {stock['s']} stock.")

        else:
            stock_obj = Stock(
                ticker=stock_info.get("symbol"),
                company_name=stock_info.get("longName"),
                description=stock_info.get("longBusinessSummary"),
                sector=stock_info.get("sector"),
                industry=stock_info.get("industry"),
                exchange={
                    "name": stock_info.get("fullExchangeName"),
                    "symbol": stock_info.get("exchange"),
                },
                logo_url=f"https://logos.stockanalysis.com/{stock.get('s', '').lower()}.svg",
                website=stock_info.get("website"),
                locale=stock_info.get("region"),
                country=stock_info.get("country"),
                address={
                    "street": stock_info.get("address1"),
                    "city": stock_info.get("city"),
                    "state": stock_info.get("state"),
                    "zip_code": stock_info.get("zip"),
                },
                phone=stock_info.get("phone"),
                employees=stock_info.get("fullTimeEmployees"),
                company_officers=stock_info.get("companyOfficers"),
                currency=stock_info.get("currency"),
                market_cap=stock_info.get("marketCap"),
            )
            stock_obj.save()

            logger.info(f"Saved {stock['s']} stock.")

    logger.info("=" * 50)
    logger.info("Scraping Stocks Completed")
    logger.info("=" * 50)


def main():
    schedule.every(5).seconds.do(scrape_stocks)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
