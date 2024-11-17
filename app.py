from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
import chromedriver_autoinstaller
import logging
from urllib.parse import urlparse
import re
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Automatically install the appropriate ChromeDriver
chromedriver_autoinstaller.install()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://first-link-delta.vercel.app").split(",")
CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

# App configurations
app.config.update({
    "ENV": os.getenv("FLASK_ENV", "production"),
    "SECRET_KEY": os.getenv("SECRET_KEY", "default_secret_key"),
    "MAX_ITERATIONS": int(os.getenv("MAX_ITERATIONS", 15)),
    "PHILOSOPHY_URL": "https://en.wikipedia.org/wiki/Philosophy",
    "SELENIUM_WAIT_TIME": 10,
})

# Validate Wikipedia URLs
def is_valid_wikipedia_url(url):
    regex = r"^https?://en.wikipedia.org/wiki/[^ ]+$"
    return bool(re.match(regex, url))

# Setup Chrome driver
def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

# Find the first valid Wikipedia anchor link in the content
def find_first_anchor(driver):
    try:
        paragraphs = WebDriverWait(driver, app.config["SELENIUM_WAIT_TIME"]).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@id='mw-content-text']//p[not(contains(@class, 'mw-empty-elt'))]"))
        )

        for paragraph in paragraphs:
            anchors = paragraph.find_elements(By.XPATH, "./a[not(ancestor::span) and not(ancestor::sup)]")
            for anchor in anchors:
                anchor_link = anchor.get_attribute("href")
                if anchor_link and anchor_link.startswith("https://en.wikipedia.org/wiki/") and not anchor_link.startswith("https://en.wikipedia.org/wiki/Help:"):
                    return anchor_link
        return None
    except Exception as e:
        logging.error(f"Error finding anchor: {e}")
        return None

# Traverse Wikipedia pages
def traverse_wikipedia(start_url, max_iterations):
    driver = setup_driver()
    visited_urls = set()
    results = {"path": [], "steps": 0, "last_link": None}

    try:
        current_url = start_url

        for step in range(max_iterations):
            if current_url in visited_urls:
                return {**results, "error": f"Traversal ended in a loop at: {current_url}"}

            visited_urls.add(current_url)
            results["path"].append(current_url)

            if current_url == app.config["PHILOSOPHY_URL"]:
                results.update({"steps": step + 1, "last_link": current_url})
                return results

            driver.get(current_url)
            next_url = find_first_anchor(driver)

            if not next_url:
                return {**results, "error": "No valid anchor link found in content."}

            current_url = next_url

        return {**results, "error": "Maximum iterations reached.", "visited_count": len(visited_urls)}
    except TimeoutException as e:
        logging.error(f"Timeout error while loading {current_url}: {e}")
        return {**results, "error": "Timeout while loading page."}
    except NoSuchElementException as e:
        logging.error(f"Element not found on page {current_url}: {e}")
        return {**results, "error": "Anchor element not found on the page."}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {**results, "error": "An unexpected error occurred."}
    finally:
        driver.quit()

# API endpoint to start traversal
@app.route("/start-traversal", methods=["POST"])
def start_traversal():
    data = request.get_json()
    start_url = data.get("start_url")

    if not start_url or not is_valid_wikipedia_url(start_url):
        return jsonify({"error": "A valid Wikipedia URL is required."}), 400

    max_iterations = app.config["MAX_ITERATIONS"]
    result = traverse_wikipedia(start_url, max_iterations)
    return jsonify(result)

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Run the app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
