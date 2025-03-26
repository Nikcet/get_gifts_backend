from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import NoSuchElementException
import random
import time
import re

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
    name: str = ""
    photo: str = ""
    cost: float = 0.0

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    wait = WebDriverWait(
        driver, timeout=3, poll_frequency=0.5, ignored_exceptions=errors
    )
    wait.until(
        lambda d: (
            d.find_element(By.TAG_NAME, "h1").is_displayed(),
            d.find_element(By.CSS_SELECTOR, ".b933-a").is_displayed(),
        )
    )
    driver.execute_script(
        f"window.scrollTo({random.randint(1, 100)}, {random.randint(100, 1000)});"
    )

    name_element = ""
    photo_element = ""
    cost_element = ""

    try:
        name_element = driver.find_element(By.TAG_NAME, "h1")
    except Exception as e:
        print(f"Dont find a title: {e}")

    try:
        photo_element = driver.find_element(
            By.XPATH, '//img[@data-lcp-name="webGallery-3311626-default-1"]'
        )
    except Exception as e:
        print(f"Dont find a photo link: {e}")
        print("Try other way...")
        try:
            photo_element = driver.find_element(
                By.XPATH, '//img[@data-lcp-name="webGallery-3311629-default-1"]'
            )
        except Exception as e:
            print(f"Dont find a photo link: {e}")
    try:
        cost_element = (
            driver.find_element(By.XPATH, '//button[contains(@class, "a2020-a4")]')
            .find_element(By.XPATH, ".//span")
            .find_element(By.XPATH, ".//span")
        )
    except Exception as e:
        print(f"Dont find a cost: {e}")
        print("Try other way...")
        try:
            cost_element = (
                driver.find_element(By.XPATH, '//div[contains(@data-widget, "webPrice")]')
                .find_element(By.XPATH, ".//div")
                .find_element(By.XPATH, ".//div")
                .find_element(By.XPATH, ".//div")
                .find_element(By.XPATH, ".//div")
                .find_element(By.XPATH, ".//span")
            )
        except Exception as e:
            print(f"Dont find a cost: {e}")

    if name_element:
        name = name_element.text

    if photo_element:
        photo = photo_element.get_attribute("src")

    if cost_element:
        cost = float(re.sub(r"[^\d,]", "", cost_element.text).replace(",", "."))

    driver.quit()
    return {"name": name, "photo": photo, "cost": cost}
