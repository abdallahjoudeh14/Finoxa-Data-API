import os
import sys
import time
import logging

import schedule
import yfinance as yf

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from models.index_model import Index

from configs.db import connect_db
from utils.logger_util import logger


LOG_SCRAPER_FILE = os.path.join(os.getcwd(), r"logs\indices_scraper.log")

file_handler = logging.FileHandler(filename=LOG_SCRAPER_FILE)
file_handler.setFormatter(
    logging.Formatter("[%(asctime)s] - [%(levelname)s] - %(message)s")
)
logger.addHandler(file_handler)

indices_symbols = [
    "^GSPC",
    "^DJI",
    "^IXIC",
    "^NYA",
    "^XAX",
    "^BUK100P",
    "^RUT",
    "^VIX",
    "^FTSE",
    "^GDAXI",
    "^FCHI",
    "^STOXX50E",
    "^N100",
    "^BFX",
    "MOEK.ME",
    "^HSI",
    "^STI",
    "^AXJD",
    "^AORD",
    "^BSESN",
    "^JKSE",
    "^KLSE",
    "^NZ50",
    "^KS11",
    "^TWII",
    "^GSPTSE",
    "^BVSP",
    "^MXX",
    "^IPSA",
    "^MERV",
    "^TA125.TA",
    "^CASE30",
    "^JNOUJO",
    "DXY.NVB",
    "^125904-USD-STRD",
    "^XDB",
    "^XDE",
    "000001.SS",
    "^N225",
    "^XDN",
    "^XDA",
]


def scrape_indices():
    connect_db()

    logger.info("=" * 50)
    logger.info("Starting Indices Scraper")
    logger.info("=" * 50)

    for index in indices_symbols:
        logger.info(f"Scraping {index} index")
        try:
            if Index.objects(ticker=index):
                continue
            else:
                index_info = yf.Ticker(index).info
                index_obj = Index(
                    ticker=index_info.get("symbol"),
                    name=index_info.get("shortName"),
                    exchange_name=index_info.get("fullExchangeName"),
                    exchange=index_info.get("exchange"),
                    locale=index_info.get("region"),
                    currency=index_info.get("currency"),
                )
                index_obj.save()
                logger.info(f"Saved {index} index")

            time.sleep(5)
        except Exception as e:
            logger.error(f"Error scraping {index} index: {e}")

    logger.info("=" * 50)
    logger.info("Scraping Indices Completed")
    logger.info("=" * 50)


def main():

    schedule.every(5).minutes.do(scrape_indices)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
