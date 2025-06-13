# pip modules
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def setup_driver(headless=True) -> webdriver.Chrome:
    """Set up and return a Chrome WebDriver.

    Args:
        headless (bool): Whether to run Chrome in headless mode

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"

    # Configure Chrome options
    chrome_options = Options()

    if headless:
        chrome_options.add_argument("--headless")

    chrome_options.add_argument(f"user-agent={USER_AGENT}")
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Initialize the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)
    return driver
