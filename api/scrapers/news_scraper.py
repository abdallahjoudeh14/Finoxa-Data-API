# built-in modules
import os
import sys
import time
import logging
import schedule


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# custom modules
from google_news import GoogleNews
from models.newsArticle_model import NewsArticle
from configs.db import connect_db
from utils.logger_util import logger

from pipelines.summarization import Summarizer
from pipelines.ticker_validation import TickerValidator
from pipelines.prediction import Prediction

LOG_SCRAPER_FILE = os.path.join(os.getcwd(), r"api\logs\news_scraper.log")

file_handler = logging.FileHandler(filename=LOG_SCRAPER_FILE)
file_handler.setFormatter(
    logging.Formatter("[%(asctime)s] - [%(levelname)s] - %(message)s")
)
logger.addHandler(file_handler)


def scrape_news():
    connect_db()

    logger.info("=" * 50)
    logger.info("Starting Google News Scraper")
    logger.info("=" * 50)

    topic = "business"
    logger.info("Running example search for topic: '%s'", topic)

    start_time = time.time()
    gn = GoogleNews()
    results = gn.topic(topic=topic)

    elapsed_time = time.time() - start_time

    logger.info("Scrape completed in %.2f seconds", elapsed_time)

    logger.info("Found %d articles about '%s':", len(results), topic)

    model_path = "abdallahjoudeh/finoxa-model"

    summarizer = Summarizer()
    validator = TickerValidator()
    prediction = Prediction(model_path)

    for article in results:
        if NewsArticle.objects(article_url=article["article_url"]).first():
            continue

        summary_sentences = summarizer.summarize(article["content"])
        ticker_sentences = []

        tickers = []
        insights = []

        for sentence in summary_sentences:
            ticker_info = validator.validate(sentence)
            if ticker_info.get("validated_companies"):
                if len(ticker_info["validated_companies"]):
                    ticker_sentences.append(
                        {
                            "sentence": sentence,
                            "ticker": ticker_info["validated_companies"][0]["ticker"],
                        }
                    )

        for ticker_sentence in ticker_sentences:
            tickers.append(ticker_sentence["ticker"])
            sentiment_info = prediction.predict(ticker_sentence["sentence"])
            sentiment = sentiment_info["sentiment"]
            sentiment_reasoning = ticker_sentence["sentence"]
            sentiment_score = sentiment_info["score"]
            insights.append(
                {
                    "ticker": ticker_sentence["ticker"],
                    "sentiment": sentiment,
                    "sentiment_reasoning": sentiment_reasoning,
                    "sentiment_score": sentiment_score,
                }
            )

        news_article = NewsArticle(
            title=article["title"],
            description="",
            article_url=article["article_url"],
            image_url=article["image_url"],
            authors=article["authors"],
            published_at=article["published_at"],
            publisher={
                "name": article["publisher"]["name"],
                "homepage_url": article["publisher"]["homepage_url"],
                "logo_url": article["publisher"]["logo_url"],
            },
            tickers=tickers,
            insights=insights,
        )

        news_article.save()

        logger.info(f"Saved {news_article.title} news article")

    logger.info("=" * 50)
    logger.info("Google News Scraper Finished")
    logger.info("=" * 50)


if __name__ == "__main__":
    schedule.every(15).minutes.do(scrape_news)
    while True:
        schedule.run_pending()
        time.sleep(1)
