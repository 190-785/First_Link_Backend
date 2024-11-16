from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
import chromedriver_autoinstaller
import logging
from urllib.parse import urlparse

# Automatically install the appropriate ChromeDriver
chromedriver_autoinstaller.install()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(
    app,
    origins=["https://first-link-delta.vercel.app"],
    methods=["GET", "POST"],
    supports_credentials=True,
)

# Set app configurations
app.config["ENV"] = os.getenv("FLASK_ENV", "production")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")

# Helper function to validate URLs
def is_valid_wikipedia_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ["http", "https"] and "en.wikipedia.org" in parsed_url.netloc

# Main Wikipedia traversal function
def start_wiki_traversal(start_url, max_iterations=50):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    current_website = start_url
    results = {"path": [], "steps": 0, "last_link": None}
    visited_urls = set()
    loop_counter = 0

    try:
        while current_website != "https://en.wikipedia.org/wiki/Philosophy":
            if current_website in visited_urls:
                results["path"].append(current_website)
                results["error"] = f"Traversal ended in a loop at: {current_website}"
                break

            visited_urls.add(current_website)
            results["path"].append(current_website)

            if loop_counter >= max_iterations:
                results["error"] = "Maximum iterations reached, traversal stopped."
                break

            loop_counter += 1
            results["steps"] += 1

            driver.get(current_website)

            paragraphs = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//div[@id='mw-content-text' and contains(@class, 'mw-body-content')]//p[not(contains(@class, 'mw-empty-elt'))]",
                    )
                )
            )

            first_anchor_found = False
            for paragraph in paragraphs:
                anchors = paragraph.find_elements(
                    By.XPATH,
                    "./a[not(ancestor::span) and not(ancestor::sup)]",
                )
                for anchor in anchors:
                    anchor_link = anchor.get_attribute("href")
                    if anchor_link.startswith("https://en.wikipedia.org/wiki/Help:"):
                        continue
                    current_website = anchor_link
                    results["last_link"] = current_website
                    first_anchor_found = True
                    break
                if first_anchor_found:
                    break

            if not first_anchor_found:
                results["error"] = "No valid direct anchor tag found in any paragraph."
                break
    except Exception as e:
        logging.error(f"Error during traversal: {str(e)}")
        results["error"] = f"An error occurred: {str(e)}"
    finally:
        driver.quit()

    return results

# API endpoint to start traversal
@app.route("/start-traversal", methods=["POST"])
def traverse_wikipedia():
    try:
        data = request.get_json()
        start_url = data.get("start_url")

        if not start_url or not is_valid_wikipedia_url(start_url):
            return jsonify({"error": "A valid Wikipedia URL is required."}), 400

        max_iterations = int(os.getenv("MAX_ITERATIONS", 50))
        result = start_wiki_traversal(start_url, max_iterations)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    try:
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        logging.error(f"Health check error: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
