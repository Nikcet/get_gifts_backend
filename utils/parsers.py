from seleniumbase import SB
from selenium.common import NoSuchElementException
import re

from . import logger

headers = "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3&accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
errors = [NoSuchElementException]


def parse_url_ozon(url: str):
    logger.info("_____________________________________________")
    logger.info("Start to parse OZON.")
    name: str = ""
    photo: str = ""
    cost: float = 0.0
    cost_element = ""

    with SB(uc=True, headless=True) as sb:
        sb.open(url)
        sb.sleep(2)
        logger.info("Trying to find title.")

        try:
            name = sb.get_text("h1")
            logger.info(f"Found title: {name}")
        except Exception as e:
            logger.error(f"Find title failed: {e}")

        logger.info("Trying to find photo.")
        photo_selectors = [
            'img[src*="cover.jpg"][loading="eager"]',
            'img[data-lcp-name="webGallery-3311626-default-1"]',
            'img[data-lcp-name="webGallery-3311629-default-1"]',
        ]

        for selector in photo_selectors:
            try:
                photo = sb.get_attribute(selector, "src", timeout=2)
                if photo:
                    if "cover" in selector:
                        logger.info("Video detected. Clicking on data-index=1 element.")
                        try:
                            sb.click('div[data-index="1"]')
                            continue
                        except Exception as e:
                            logger.error(f"Click failed: {e}")

                    logger.info(f"Found photo: {photo}")
                    break
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue

        logger.info("Trying to find price.")
        try:
            cost_element = sb.find_element('button[class*="a2020-a4"] span span', timeout=2)
            logger.debug("Find cost (method 1): Success.")
        except Exception as e:
            logger.debug(f"Find cost (method 1): Failed. Error: {e}")
            logger.debug("Try to find other cost.")
            try:
                cost_element = sb.find_element(
                    'div[data-widget*="webPrice"] div div div div span', timeout=2
                )
                logger.debug("Find cost (method 2): Success.")
            except Exception as e:
                logger.debug(f"Find cost (method 2): Failed. Error: {e}")
                cost = 0.0

        if cost_element:
            cost = float(re.sub(r"[^\d,]", "", cost_element.text).replace(",", "."))

    return {"name": name, "photo": photo, "cost": cost}
