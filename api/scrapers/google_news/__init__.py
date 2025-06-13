# built-in modules
import os
import sys
import time
import logging
from typing import List, Dict

# pip modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from newspaper import Article
from goose3 import Goose
from urllib.parse import quote, urlparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# custom modules
from scrapers.google_news.utils import get_topic_id, topic_url
from scrapers.google_news.driver import setup_driver
from utils.logger_util import logger

LOG_SCRAPER_FILE = os.path.join(os.getcwd(), r"api\logs\news_scraper.log")

logger.addHandler(logging.FileHandler(LOG_SCRAPER_FILE))

_SELECTORS = {
    "article": "article.UwIKyb",
    "title": ".gPFEn",
    "link": "a.WwrzSb",
    "time": "time.hvbAAd",
    "author": [".bInasb > span", ".MkYNL.v6lQ3b > span"],
    "publisher_img": [".MCAGUe img.qEdqNd", ".oovtQ img.qEdqNd"],
    "publisher_name": [".MCAGUe .a7P8l .vr1PYe", ".oovtQ .a7P8l .vr1PYe"],
}

_SELECTORS_SEARCH = {
    "article": "article.IFHyqb",
    "title": ".JtKRv",
    "link": "a.WwrzSb",
    "time": "time.hvbAAd",
    "author": ".bInasb > span",
    "publisher_img": ".MCAGUe img.qEdqNd",
    "publisher_name": ".MCAGUe .a7P8l .vr1PYe",
}


class GoogleNews:
    def __init__(self, lang: str = "en", country: str = "US"):
        self._lang = lang
        self._country = country
        self._driver = setup_driver(headless=True)

    def topic(self, topic: str) -> List[Dict]:
        topic_id = get_topic_id(topic=topic)
        url = topic_url(topic_id=topic_id, lang=self._lang, country=self._country)
        logger.info(f"Navigating to URL: {url}")

        self._driver.get(url)
        self._driver.implicitly_wait(10)

        article_elements = self._find_article_elements()
        logger.info(f"Found {len(article_elements)} article elements")

        articles = []
        count = 0

        for article_element in article_elements:
            if count >= len(article_elements):
                break

            try:
                logger.info(f"Processing article {count+1}/{len(article_elements)}")
                article_data = self._extract_article_metadata(
                    article_element, type="topic"
                )
                logger.info(f"Extracted metadata for article: {article_data['title']}")

                logger.info(f"Fetching content from: {article_data['article_url']}")
                article_content = self._extract_article_content(
                    article_data["article_url"]
                )

                if article_content:
                    article_data.update(article_content)
                    articles.append(article_data)
                    logger.info(f"Successfully added article: {article_data['title']}")
                else:
                    logger.warning(
                        f"Failed to scrape article content: {article_data['title']}"
                    )
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
            count += 1

        self._driver.quit()

        return articles

    def search(self, query: str) -> List[Dict]:
        """Search for articles based on a query string."""
        logger.info(f"Searching for articles with query: {query}")
        encoded_query = quote(query)
        url = f"https://news.google.com/search?q={encoded_query}&hl={self._lang}-{self._country}&gl={self._country}&ceid={self._country}:{self._lang}"
        logger.info(f"Navigating to search URL: {url}")

        self._driver.get(url)
        self._driver.implicitly_wait(10)

        article_elements = self._find_article_elements(type="search")
        logger.info(f"Found {len(article_elements)} search result articles")

        articles = []
        count = 0

        for article_element in article_elements:
            if count >= len(article_elements):
                break

            try:
                logger.info(
                    f"Processing search result {count+1}/{len(article_elements)}"
                )
                article_data = self._extract_article_metadata(
                    article_element, type="search"
                )
                logger.info(
                    f"Extracted metadata for search result: {article_data['title']}"
                )

                logger.info(f"Fetching content from: {article_data['article_url']}")
                article_content = self._extract_article_content(
                    article_data["article_url"]
                )

                if article_content:
                    article_data.update(article_content)
                    articles.append(article_data)
                    logger.info(
                        f"Successfully added search result: {article_data['title']}"
                    )
                    count += 1
                else:
                    logger.warning(
                        f"Failed to scrape search result content: {article_data['title']}"
                    )
            except Exception as e:
                logger.error(f"Error processing search result: {str(e)}")

        self._driver.quit()

        return articles

    def _find_article_elements(self, type: str = "topic") -> List[WebElement]:
        """Find article elements on the page on the google news page.

        Args:
            type (str, optional): Type of page to scrape. Defaults to "topic".

        Returns:
            List[WebElement]: List of article elements found on the page.
        """

        article_elements = self._driver.find_elements(
            by=By.CSS_SELECTOR,
            value=(
                _SELECTORS["article"]
                if type == "topic"
                else _SELECTORS_SEARCH["article"]
            ),
        )
        return article_elements

    def _extract_article_metadata(
        self, article_element: WebElement, type: str = "topic"
    ) -> Dict:
        """Extract metadata from the article element.
        This includes title, source URL, published date, authors, and publisher.

        Args:
            article_element (WebElement): The article element to extract metadata from.
            type (str, optional): Type of page to scrape. Defaults to "topic".

        Returns:
            Dict: Dictionary containing metadata extracted from the article element.
        """
        article_metadata = {
            "title": "",
            "article_url": "",
            "published_at": "",
            "authors": [],
            "publisher": {},
        }

        article_metadata["title"] = article_element.find_element(
            by=By.CSS_SELECTOR,
            value=(
                _SELECTORS["title"] if type == "topic" else _SELECTORS_SEARCH["title"]
            ),
        ).text

        redirect_url = article_element.find_element(
            by=By.CSS_SELECTOR,
            value=_SELECTORS["link"] if type == "topic" else _SELECTORS_SEARCH["link"],
        ).get_attribute("href")

        time.sleep(5)
        article_metadata["article_url"] = self._get_article_url(redirect_url)

        article_metadata["published_at"] = article_element.find_element(
            by=By.CSS_SELECTOR,
            value=_SELECTORS["time"] if type == "topic" else _SELECTORS_SEARCH["time"],
        ).get_attribute("datetime")

        try:
            author_element = article_element.find_element(
                by=By.CSS_SELECTOR,
                value=(
                    _SELECTORS["author"][0]
                    if type == "topic"
                    else _SELECTORS_SEARCH["author"]
                ),
            )
            article_metadata["authors"] = [
                *map(
                    lambda author: author.strip(),
                    author_element.text.replace("By ", "").replace("&", ",").split(","),
                )
            ]
        except Exception:
            try:
                author_element = article_element.find_element(
                    by=By.CSS_SELECTOR,
                    value=(
                        _SELECTORS["author"][1]
                        if type == "topic"
                        else _SELECTORS_SEARCH["author"]
                    ),
                )
                article_metadata["authors"] = [
                    *map(
                        lambda author: author.strip(),
                        author_element.text.replace("By ", "")
                        .replace("&", ",")
                        .split(","),
                    )
                ]
            except Exception:
                article_metadata["authors"] = []

        try:
            article_metadata["publisher"]["name"] = article_element.find_element(
                by=By.CSS_SELECTOR,
                value=(
                    _SELECTORS["publisher_name"][0]
                    if type == "topic"
                    else _SELECTORS_SEARCH["publisher_name"]
                ),
            ).text.strip()
        except Exception:
            article_metadata["publisher"]["name"] = article_element.find_element(
                by=By.CSS_SELECTOR,
                value=(
                    _SELECTORS["publisher_name"][1]
                    if type == "topic"
                    else _SELECTORS_SEARCH["publisher_name"]
                ),
            ).text.strip()

        article_metadata["publisher"]["homepage_url"] = urlparse(
            article_metadata["article_url"]
        ).netloc

        try:
            article_metadata["publisher"]["logo_url"] = article_element.find_element(
                by=By.CSS_SELECTOR,
                value=(
                    _SELECTORS["publisher_img"][0]
                    if type == "topic"
                    else _SELECTORS_SEARCH["publisher_img"]
                ),
            ).get_attribute("src")
        except Exception:
            article_metadata["publisher"]["logo_url"] = article_element.find_element(
                by=By.CSS_SELECTOR,
                value=(
                    _SELECTORS["publisher_img"][1]
                    if type == "topic"
                    else _SELECTORS_SEARCH["publisher_img"]
                ),
            ).get_attribute("src")

        return article_metadata

    def _extract_article_content(self, url: str) -> Dict | None:
        """Fetch and parse the full article content from the source URL.

        Args:
            url (str): URL of the original article

        Returns:
            Dict: Dictionary containing the article content and image
        """

        content_data = {"content": "", "image_url": ""}

        if not url:
            return content_data

        try:
            g = Goose()
            article = Article(url=url)
            article_goose = g.extract(url=url)
            article.download()
            article.parse()
            content_data["content"] = article_goose.cleaned_text
            content_data["image_url"] = article.top_image
            return content_data
        except Exception as e:
            return None

    def _get_article_url(self, redirect_url: str) -> str:
        """Extract the real URL from a redirection URL using Selenium.

        Args:
            redirect_url (str): Redirect URL

        Returns:
            str: The actual URL after redirection
        """

        try:
            # Store the current window handle
            original_window = self._driver.current_window_handle

            # Open new tab
            self._driver.switch_to.new_window("tab")

            self._driver.get(redirect_url)
            WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(5)
            article_url = self._driver.current_url

            # Close the tab and switch back to original window
            self._driver.close()
            self._driver.switch_to.window(original_window)

            return article_url
        except Exception as e:
            # Make sure to switch back to original window even if there's an error
            if len(self._driver.window_handles) > 1:
                self._driver.close()
                self.driver.switch_to.window(original_window)
            return None
