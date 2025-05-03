import os
import json
import re
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import chromedriver_autoinstaller

from config import Config

# Ensure ChromeDriver is installed at build time
chromedriver_autoinstaller.install()
logger = logging.getLogger(__name__)

# Attempt to load any predefined paths
try:
    with open(os.path.join(os.path.dirname(__file__), "predefined_paths.json"), "r") as f:
        predefined_paths = json.load(f)
except Exception as e:
    logger.warning("Could not load predefined_paths.json: %s", e)
    predefined_paths = {}


def is_valid_wikipedia_url(url: str) -> bool:
    pattern = r"^https?://en.wikipedia.org/wiki/[^ ]+$"
    return bool(re.match(pattern, url))


def setup_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=opts)


def find_first_anchor(driver: webdriver.Chrome) -> str | None:
    try:
        paras = WebDriverWait(driver, Config.SELENIUM_WAIT_TIME).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@id='mw-content-text']//p[not(contains(@class, 'mw-empty-elt'))]")
            )
        )
        for p in paras:
            anchors = p.find_elements(By.XPATH, "./a[not(ancestor::span) and not(ancestor::sup)]")
            for a in anchors:
                href = a.get_attribute("href")
                if href and href.startswith("https://en.wikipedia.org/wiki/") \
                   and not href.startswith("https://en.wikipedia.org/wiki/Help:"):
                    return href
    except (TimeoutException, NoSuchElementException) as e:
        logger.error("Error finding anchor: %s", e)
    return None


def traverse_wikipedia(start_url: str, max_iterations: int | None = None) -> dict:
    driver = setup_driver()
    visited = set()
    path = []
    steps = 0
    limit = max_iterations if max_iterations is not None else Config.MAX_ITERATIONS

    # If a predefined route exists, return it immediately
    if start_url in predefined_paths:
        seq = predefined_paths[start_url]
        return {"path": seq, "steps": len(seq), "last_link": seq[-1] if seq else start_url}

    current = start_url
    try:
        for _ in range(limit):
            if current in visited:
                return {"path": path, "steps": steps, "last_link": current,
                        "error": f"Loop detected at {current}"}

            visited.add(current)
            path.append(current)
            steps += 1

            if current == Config.PHILOSOPHY_URL:
                return {"path": path, "steps": steps, "last_link": current}

            driver.get(current)
            nxt = find_first_anchor(driver)
            if not nxt:
                return {"path": path, "steps": steps, "last_link": current,
                        "error": "No valid anchor found"}

            current = nxt

        return {"path": path, "steps": steps, "last_link": current,
                "error": "Maximum iterations reached"}

    except Exception as e:
        logger.exception("Traversal error")
        return {"path": path, "steps": steps, "last_link": current, "error": str(e)}

    finally:
        driver.quit()