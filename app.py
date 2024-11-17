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
    "MAX_ITERATIONS": int(os.getenv("MAX_ITERATIONS", 30)),
    "PHILOSOPHY_URL": "https://en.wikipedia.org/wiki/Philosophy",
    "SELENIUM_WAIT_TIME": 10,
})

predefined_paths = {
    # Physics Path
    "https://en.wikipedia.org/wiki/Physics": [
        "https://en.wikipedia.org/wiki/Scientific",
        "https://en.wikipedia.org/wiki/Scientific_method",
        "https://en.wikipedia.org/wiki/Empirical_evidence",
        "https://en.wikipedia.org/wiki/Evidence",
        "https://en.wikipedia.org/wiki/Proposition",
        "https://en.wikipedia.org/wiki/Philosophy_of_language",
        "https://en.wikipedia.org/wiki/Language"
    ],

    # Language Path
    "https://en.wikipedia.org/wiki/Language": [
        "https://en.wikipedia.org/wiki/Communication",
        "https://en.wikipedia.org/wiki/Information",
        "https://en.wikipedia.org/wiki/Abstraction",
        "https://en.wikipedia.org/wiki/Rule_of_inference",
        "https://en.wikipedia.org/wiki/Logic",
        "https://en.wikipedia.org/wiki/Logical_reasoning",
        "https://en.wikipedia.org/wiki/Mind",
        "https://en.wikipedia.org/wiki/Thought",
        "https://en.wikipedia.org/wiki/Cognition",
        "https://en.wikipedia.org/wiki/Action_(philosophy)",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Psychology Path
    "https://en.wikipedia.org/wiki/Psychology": [
        "https://en.wikipedia.org/wiki/Mind",
        "https://en.wikipedia.org/wiki/Thought",
        "https://en.wikipedia.org/wiki/Cognition",
        "https://en.wikipedia.org/wiki/Action_(philosophy)",
        "https://en.wikipedia.org/wiki/Philosophy"
    ],

    # Sports Path
    "https://en.wikipedia.org/wiki/Sport": [
        "https://en.wikipedia.org/wiki/Physical_activity",
        "https://en.wikipedia.org/wiki/Skeletal_muscle",
        "https://en.wikipedia.org/wiki/Vertebrate",
        "https://en.wikipedia.org/wiki/Deuterostome",
        "https://en.wikipedia.org/wiki/Bilateria",
        "https://en.wikipedia.org/wiki/Clade",
        "https://en.wikipedia.org/wiki/Phylogenetics",
        "https://en.wikipedia.org/wiki/Biology"
    ],

    # Biology Path
    "https://en.wikipedia.org/wiki/Biology": [
        "https://en.wikipedia.org/wiki/Life",
        "https://en.wikipedia.org/wiki/Matter",
        "https://en.wikipedia.org/wiki/Classical_physics",
        "https://en.wikipedia.org/wiki/Physics"
    ],

    # History Path
    "https://en.wikipedia.org/wiki/History": [
        "https://en.wikipedia.org/wiki/Ancient_Greek",
        "https://en.wikipedia.org/wiki/Greek_language",
        "https://en.wikipedia.org/wiki/Ancient_Greek"
    ],

    # Chemistry Path
    "https://en.wikipedia.org/wiki/Chemistry": [
        "https://en.wikipedia.org/wiki/Matter",
        "https://en.wikipedia.org/wiki/Classical_physics",
        "https://en.wikipedia.org/wiki/Physics"
    ],

    # Politics Path
    "https://en.wikipedia.org/wiki/Politics": [
        "https://en.wikipedia.org/wiki/Decision-making",
        "https://en.wikipedia.org/wiki/Psychology"
    ],

    # India Path
    "https://en.wikipedia.org/wiki/India": [
        "https://en.wikipedia.org/wiki/South_Asia",
        "https://en.wikipedia.org/wiki/Subregion#Asia",
        "https://en.wikipedia.org/wiki/Region",
        "https://en.wikipedia.org/wiki/Geography",
        "https://en.wikipedia.org/wiki/Earth",
        "https://en.wikipedia.org/wiki/Planet",
        "https://en.wikipedia.org/wiki/Hydrostatic_equilibrium",
        "https://en.wikipedia.org/wiki/Fluid_mechanics",
        "https://en.wikipedia.org/wiki/Physics"
    ],

    # Philosophy Path
    "https://en.wikipedia.org/wiki/Philosophy": [
        "https://en.wikipedia.org/wiki/Existence",
        "https://en.wikipedia.org/wiki/Reality",
        "https://en.wikipedia.org/wiki/Universe",
        "https://en.wikipedia.org/wiki/Space",
        "https://en.wikipedia.org/wiki/Three-dimensional_space",
        "https://en.wikipedia.org/wiki/Geometry",
        "https://en.wikipedia.org/wiki/Mathematics",
        "https://en.wikipedia.org/wiki/Theory",
        "https://en.wikipedia.org/wiki/Reason",
        "https://en.wikipedia.org/wiki/Consciousness",
        "https://en.wikipedia.org/wiki/Awareness",
        "https://en.wikipedia.org/wiki/Philosophy"
    ]
}

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

    # Check if starting from Philosophy and return the predefined Philosophy path directly
    if start_url == "https://en.wikipedia.org/wiki/Philosophy":
        results.update({"path": predefined_paths[start_url], "steps": len(predefined_paths[start_url]), "last_link": predefined_paths[start_url][-1]})
        return results

    try:
        current_url = start_url

        for step in range(max_iterations):
            # Check if current URL matches a predefined path
            if current_url in predefined_paths:
                predefined_path = predefined_paths[current_url]
                
                # Avoid adding the same URL if it's already in the visited path
                for url in predefined_path:
                    if url not in visited_urls:
                        visited_urls.add(url)
                        results["path"].append(url)
                        results["steps"] += 1
                        current_url = url  # Move to the next URL in the predefined path
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
    finally:
        driver.quit()



# Handle CORS preflight (OPTIONS request)
@app.before_request
def before_request():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = os.getenv("ALLOWED_ORIGINS", "https://first-link-delta.vercel.app")
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        return response

# Route to start traversal
@app.route("/start-traversal", methods=["POST"])
def start_traversal():
    data = request.get_json()
    start_url = data.get("start_url", app.config["PHILOSOPHY_URL"])

    if not is_valid_wikipedia_url(start_url):
        return jsonify({"error": "Invalid Wikipedia URL"}), 400

    result = traverse_wikipedia(start_url, app.config["MAX_ITERATIONS"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)