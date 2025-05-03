import json

from flask import Flask, jsonify, request, make_response
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
import re
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import chromedriver_autoinstaller

# Automatically install the appropriate ChromeDriver
chromedriver_autoinstaller.install()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load allowed origins for CORS from environment variable, split by comma
allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://first-link-delta.vercel.app").split(",")
CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

# App configurations loaded from environment variables with defaults
app.config.update({
    "ENV": os.getenv("FLASK_ENV", "production"),
    "SECRET_KEY": os.getenv("SECRET_KEY", "default_secret_key"),
    "MAX_ITERATIONS": int(os.getenv("MAX_ITERATIONS", 30)),
    "PHILOSOPHY_URL": "https://en.wikipedia.org/wiki/Philosophy",
    "SELENIUM_WAIT_TIME": 10,
})

# Load predefined paths from external JSON file for better maintainability
try:
    with open("predefined_paths.json", "r") as f:
        predefined_paths = json.load(f)
except Exception as e:
    logging.error(f"Failed to load predefined paths: {e}")
    predefined_paths = {}

def is_valid_wikipedia_url(url: str) -> bool:
    """
    Validate if the given URL is a valid Wikipedia article URL.
    """
    regex = r"^https?://en.wikipedia.org/wiki/[^ ]+$"
    return bool(re.match(regex, url))

def setup_driver() -> webdriver.Chrome:
    """
    Setup and return a headless Chrome WebDriver instance with required options.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def find_first_anchor(driver: webdriver.Chrome) -> str | None:
    """
    Find the first valid Wikipedia anchor link in the main content paragraphs.
    Returns the href string if found, else None.
    """
    try:
        paragraphs = WebDriverWait(driver, app.config["SELENIUM_WAIT_TIME"]).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@id='mw-content-text']//p[not(contains(@class, 'mw-empty-elt'))]")
            )
        )

        for paragraph in paragraphs:
            anchors = paragraph.find_elements(By.XPATH, "./a[not(ancestor::span) and not(ancestor::sup)]")
            for anchor in anchors:
                anchor_link = anchor.get_attribute("href")
                if anchor_link and anchor_link.startswith("https://en.wikipedia.org/wiki/") and not anchor_link.startswith("https://en.wikipedia.org/wiki/Help:"):
                    return anchor_link
        return None
    except (TimeoutException, NoSuchElementException) as e:
        logging.error(f"Error finding anchor: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error finding anchor: {e}")
        return None

def traverse_wikipedia(start_url: str, max_iterations: int) -> dict:
    """
    Traverse Wikipedia pages starting from start_url by following the first valid anchor link.
    Stops when Philosophy page is reached, max_iterations exceeded, or a loop is detected.
    Returns a dictionary with traversal path, steps count, last link, and error if any.
    """
    driver = setup_driver()
    visited_urls = set()
    results = {"path": [], "steps": 0, "last_link": None}

    # If starting from Philosophy, return predefined path directly
    if start_url == app.config["PHILOSOPHY_URL"]:
        results.update({
            "path": predefined_paths.get(start_url, []),
            "steps": len(predefined_paths.get(start_url, [])),
            "last_link": predefined_paths.get(start_url, [])[-1] if predefined_paths.get(start_url) else None
        })
        return results

    try:
        current_url = start_url

        for step in range(max_iterations):
            # Check if current URL matches a predefined path
            if current_url in predefined_paths:
                predefined_path = predefined_paths[current_url]

                # Add URLs from predefined path if not already visited
                for url in predefined_path:
                    if url not in visited_urls:
                        visited_urls.add(url)
                        results["path"].append(url)
                        results["steps"] += 1
                        current_url = url
                    if current_url == app.config["PHILOSOPHY_URL"]:
                        results.update({"steps": len(results["path"]), "last_link": current_url})
                        return results
                continue

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
    except TimeoutException:
        return {**results, "error": "Timed out while waiting for page content."}
    except Exception as e:
        logging.error(f"Unexpected error during traversal: {e}")
        return {**results, "error": f"Unexpected error: {e}"}
    finally:
        driver.quit()

@app.before_request
def before_request():
    """
    Handle CORS preflight OPTIONS requests by setting appropriate headers.
    """
    if request.method == "OPTIONS":
        response = make_response()
        origin = request.headers.get('Origin')
        if origin and origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = allowed_origins[0]
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        return response

@app.route("/start-traversal", methods=["POST"])
def start_traversal():
    """
    API endpoint to start Wikipedia traversal.
    Expects JSON body with 'start_url'.
    Returns JSON with traversal results or error message.
    """
    data = request.get_json()
    start_url = data.get("start_url", app.config["PHILOSOPHY_URL"])

    if not is_valid_wikipedia_url(start_url):
        return jsonify({"error": "Invalid Wikipedia URL"}), 400

    result = traverse_wikipedia(start_url, app.config["MAX_ITERATIONS"])
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
