from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import NoSuchElementException
import random
import re
import time

from loguru import logger

logger.add(
    "parser.log",
    rotation="10 MB",
    retention="15 days",
    compression="zip",
    level="DEBUG"
)

headers = "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3&accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
errors = [NoSuchElementException]

options = webdriver.ChromeOptions()
options.add_argument(headers)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")

async def parse_url_ozon(url: str):
    logger.info("_____________________________________________")
    logger.info("Start to parse OZON.")
    name: str = ""
    photo: str = ""
    cost: float = 0.0
    name_element = ""
    photo_element = ""
    cost_element = ""
    video_element = ""

    driver = webdriver.Chrome(options=options)
    logger.debug(f"Driver: {driver}")
    driver.get(url)

    # time.sleep(random.randint(2, 4))
    wait = WebDriverWait(
        driver, timeout=3, poll_frequency=0.5, ignored_exceptions=errors
    )
    try:
        logger.debug("Try to find elements.")
        wait.until(
            lambda d: (
                d.find_element(By.TAG_NAME, "h1").is_displayed(),
            )
        )
    except Exception as e:
        logger.debug(f"Find elements: Failed. Error: {e}")
        
    driver.execute_script(
        f"window.scrollTo({random.randint(1, 100)}, {random.randint(100, 1000)});"
    )

    try:
        name_element = driver.find_element(By.TAG_NAME, "h1")
    except Exception as e:
        logger.debug(f"Find title: Failed. Error: {e}")

    try:
        photo_element = driver.find_element(
            By.XPATH, '//img[@data-lcp-name="webGallery-3311626-default-1"]'
        )
        logger.debug("Find photo: Success.")
    except Exception as e:
        logger.debug(f"Find photo: Failed. Error: {e}")
        logger.debug("Try to find other photo.")
        try:
            photo_element = driver.find_element(
                By.XPATH, '//img[@data-lcp-name="webGallery-3311629-default-1"]'
            )
            logger.debug("Find photo: Success.")
        except Exception as e:
            logger.debug(f"Find photo: Failed. Error: {e}")
            try:
                # logger.debug("Try to find video element.")
                # video_element = driver.find_element(By.TAG_NAME, "video")
                # logger.debug("Find video: Success.")
                logger.debug("Try to find other photo now.")
                photo_element = driver.find_element(By.XPATH, '//img[contains(@src, "cover.jpg") and @loading="eager"]')
                logger.debug("Find photo: Success.")
            except Exception as e:
                logger.debug(f"Find video: Failed. Error: {e}")      
    try:
        cost_element = (
            driver.find_element(By.XPATH, '//button[contains(@class, "a2020-a4")]')
            .find_element(By.XPATH, ".//span")
            .find_element(By.XPATH, ".//span")
        )
        logger.debug("Find cost: Success.")
    except Exception as e:
        logger.debug(f"Find cost: Failed. Error: {e}")
        logger.debug("Try to find other cost.")
        try:
            cost_element = (
                driver.find_element(By.XPATH, '//div[contains(@data-widget, "webPrice")]')
                .find_element(By.XPATH, ".//div")
                .find_element(By.XPATH, ".//div")
                .find_element(By.XPATH, ".//div")
                .find_element(By.XPATH, ".//div")
                .find_element(By.XPATH, ".//span")
            )
            logger.debug("Find cost: Success.")
        except Exception as e:
            logger.debug(f"Find cost: Failed. Error: {e}")

    if name_element:
        name = name_element.text

    if photo_element:
        photo = photo_element.get_attribute("src")
    elif video_element:
        photo = video_element.get_attribute("src")

    if cost_element:
        cost = float(re.sub(r"[^\d,]", "", cost_element.text).replace(",", "."))

    driver.quit()
    return {"name": name, "photo": photo, "cost": cost}
